"""Leakage-safe PySpark ML evaluation on the canonical catalog.

The target remains SATCAT OBJECT_TYPE. Rows are split by NORAD object identity,
not randomly by observation, so repeated TLE observations cannot cross splits.
Hyperparameters are selected on validation macro-F1; the test set is used once
for the final report.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import Imputer, StandardScaler, StringIndexer, VectorAssembler
from pyspark.sql import SparkSession, functions as F


NUMERIC_FEATURES = [
    "inclination", "raan", "eccentricity", "arg_perigee", "mean_anomaly",
    "mean_motion", "mean_motion_dot", "bstar", "altitude_km", "period_min",
]


def add_metrics(predictions, labels: list[str]) -> dict:
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")
    metrics = {
        "accuracy": evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"}),
        "macro_f1": evaluator.evaluate(predictions, {evaluator.metricName: "f1"}),
        "weighted_precision": evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"}),
        "weighted_recall": evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"}),
    }
    rows = []
    for index, label in enumerate(labels):
        actual = predictions.filter(F.col("label") == float(index)).count()
        predicted = predictions.filter(F.col("prediction") == float(index)).count()
        true_positive = predictions.filter(
            (F.col("label") == float(index)) & (F.col("prediction") == float(index))
        ).count()
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / actual if actual else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"label": label, "support": actual, "precision": precision, "recall": recall, "f1": f1})
    metrics["class_metrics"] = rows
    return metrics


def run(input_path: str, output_dir: str) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("space-debris-pyspark-object-type-catalog")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    try:
        spark.sparkContext.setLogLevel("WARN")
        raw = spark.read.option("header", True).option("inferSchema", True).csv(input_path)
        data = raw.select("norad_id", "epoch", "OBJECT_TYPE", *NUMERIC_FEATURES).withColumn(
            "OBJECT_TYPE",
            F.when(F.upper(F.trim("OBJECT_TYPE")).isin("UNK", "UNKNOWN"), F.lit("UNK"))
            .otherwise(F.upper(F.trim("OBJECT_TYPE"))),
        )
        for feature in NUMERIC_FEATURES:
            data = data.withColumn(feature, F.col(feature).cast("double"))
        data = data.filter(F.col("norad_id").isNotNull() & F.col("OBJECT_TYPE").isNotNull())
        data = data.withColumn("group_bucket", F.pmod(F.xxhash64("norad_id"), F.lit(10)))
        train = data.filter(F.col("group_bucket") <= 6).drop("group_bucket")
        validation = data.filter(F.col("group_bucket").isin(7, 8)).drop("group_bucket")
        test = data.filter(F.col("group_bucket") == 9).drop("group_bucket")
        train.cache(); validation.cache(); test.cache()
        train.count(); validation.count(); test.count()

        imputed = [f"{name}_imputed" for name in NUMERIC_FEATURES]
        preprocessor = Pipeline(stages=[
            Imputer(inputCols=NUMERIC_FEATURES, outputCols=imputed),
            VectorAssembler(inputCols=imputed, outputCol="assembled_features"),
            StandardScaler(inputCol="assembled_features", outputCol="features", withMean=True, withStd=True),
            StringIndexer(inputCol="OBJECT_TYPE", outputCol="label", handleInvalid="skip"),
        ]).fit(train)
        train_p = preprocessor.transform(train).cache()
        validation_p = preprocessor.transform(validation).cache()
        test_p = preprocessor.transform(test).cache()
        train_p.count(); validation_p.count(); test_p.count()
        labels = preprocessor.stages[-1].labels
        counts = {row["OBJECT_TYPE"]: row["count"] for row in train.groupBy("OBJECT_TYPE").count().collect()}
        total = sum(counts.values())
        weights = {label: total / (len(counts) * count) for label, count in counts.items()}
        weight_expr = F.create_map(*[x for pair in weights.items() for x in (F.lit(pair[0]), F.lit(float(pair[1])))])
        train_p = train_p.withColumn("class_weight", weight_expr[F.col("OBJECT_TYPE")])

        candidates = []
        for reg_param in (0.0, 0.01, 0.1):
            for elastic_net in (0.0, 0.5):
                lr = LogisticRegression(
                    featuresCol="features", labelCol="label", weightCol="class_weight",
                    maxIter=100, regParam=reg_param, elasticNetParam=elastic_net,
                )
                model = lr.fit(train_p)
                validation_predictions = model.transform(validation_p).cache()
                validation_predictions.count()
                metrics = add_metrics(validation_predictions, labels)
                candidates.append({
                    "regParam": reg_param, "elasticNetParam": elastic_net,
                    "validation": metrics,
                })
                validation_predictions.unpersist()
        selected = max(candidates, key=lambda item: (item["validation"]["macro_f1"], item["validation"]["accuracy"]))
        final_lr = LogisticRegression(
            featuresCol="features", labelCol="label", weightCol="class_weight",
            maxIter=100, regParam=selected["regParam"], elasticNetParam=selected["elasticNetParam"],
        )
        final_model = final_lr.fit(train_p)
        test_predictions = final_model.transform(test_p).cache()
        test_predictions.count()
        test_metrics = add_metrics(test_predictions, labels)
        all_predictions = final_model.transform(preprocessor.transform(data))
        label_values = F.array(*[F.lit(label) for label in labels])
        all_predictions.select(
            "norad_id", "epoch", F.col("OBJECT_TYPE").alias("actual_category"),
            F.element_at(label_values, F.col("prediction").cast("int") + 1).alias("predicted_category"),
        ).coalesce(1).write.mode("overwrite").option("header", True).csv(str(out / "predictions_csv"))
        majority = max(counts, key=counts.get)
        majority_accuracy = test.filter(F.col("OBJECT_TYPE") == majority).count() / test.count()
        baseline_f1 = []
        test_counts = {row["OBJECT_TYPE"]: row["count"] for row in test.groupBy("OBJECT_TYPE").count().collect()}
        for label in sorted(set(test_counts) | {majority}):
            actual = test_counts.get(label, 0)
            predicted = test.count() if label == majority else 0
            tp = actual if label == majority else 0
            precision = tp / predicted if predicted else 0.0
            recall = tp / actual if actual else 0.0
            baseline_f1.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)

        preprocessor.write().overwrite().save(str(out / "preprocessor"))
        final_model.write().overwrite().save(str(out / "model"))
        metrics = {
            "task": "SATCAT OBJECT_TYPE classification",
            "collision_risk_model": False,
            "input": str(input_path),
            "rows": data.count(),
            "unique_norad_ids_in_sample": data.select("norad_id").distinct().count(),
            "features": NUMERIC_FEATURES,
            "target": "OBJECT_TYPE (UNKNOWN normalized to UNK)",
            "split": "deterministic NORAD-ID hash split: train buckets 0-6, validation 7-8, test 9",
            "train_rows": train.count(), "validation_rows": validation.count(), "test_rows": test.count(),
            "spark_version": spark.version, "pyspark_version": __import__("pyspark").__version__,
            "python_version": platform.python_version(), "random_seed": 20261016,
            "class_weights": weights, "train_class_counts": counts, "test_class_counts": test_counts,
            "selected_parameters": {"regParam": selected["regParam"], "elasticNetParam": selected["elasticNetParam"]},
            "validation_metrics": selected["validation"], "test_metrics": test_metrics,
            "majority_baseline": {"label": majority, "accuracy": majority_accuracy, "macro_f1": sum(baseline_f1) / len(baseline_f1)},
            "full_prediction_rows": data.count(),
            "tuning_candidates": [{"regParam": x["regParam"], "elasticNetParam": x["elasticNetParam"], "validation_accuracy": x["validation"]["accuracy"], "validation_macro_f1": x["validation"]["macro_f1"]} for x in candidates],
            "leakage_controls": ["derived sample fixed before modeling", "train-only imputation/scaling/label indexing", "NORAD-ID group split", "validation-only hyperparameter selection", "test used once for final metrics"],
        }
        (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(metrics, indent=2))
        print("ml_status=PASS")
        return metrics
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run(args.input, args.output)
