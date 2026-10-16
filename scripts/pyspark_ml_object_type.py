"""Leakage-safe PySpark ML baseline for SATCAT OBJECT_TYPE classification.

This is object-type classification, not collision-risk prediction. It reads the
bounded Parquet artifact under the external C: workspace and never reads the
large joined dataset.
"""

import argparse
import json
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml import PipelineModel
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import Imputer, StringIndexer, VectorAssembler
from pyspark.sql import SparkSession, functions as F


FEATURES = ["PERIOD", "INCLINATION", "APOGEE", "PERIGEE", "RCS"]


def classification_metrics(predictions, labels):
    """Return held-out accuracy and one-vs-rest metrics for each indexed label."""
    total = predictions.count()
    correct = predictions.filter(F.col("prediction") == F.col("label")).count()
    metrics = []
    for index, label in enumerate(labels):
        actual = predictions.filter(F.col("label") == float(index)).count()
        predicted = predictions.filter(F.col("prediction") == float(index)).count()
        true_positive = predictions.filter(
            (F.col("label") == float(index)) & (F.col("prediction") == float(index))
        ).count()
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / actual if actual else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        metrics.append({"label": label, "support": actual, "precision": precision,
                        "recall": recall, "f1": f1})
    return (correct / total if total else 0.0), metrics


def run(input_path: str, output_dir: str) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("space-debris-pyspark-object-type")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    try:
        spark.sparkContext.setLogLevel("WARN")
        data = spark.read.parquet(input_path).select(*(FEATURES + ["OBJECT_TYPE"]))
        data = data.filter(F.col("OBJECT_TYPE").isNotNull())
        train, test = data.randomSplit([0.75, 0.25], seed=42)
        imputed = [f"{name}_imputed" for name in FEATURES]
        pipeline = Pipeline(stages=[
            Imputer(inputCols=FEATURES, outputCols=imputed),
            VectorAssembler(inputCols=imputed, outputCol="features"),
            StringIndexer(inputCol="OBJECT_TYPE", outputCol="label", handleInvalid="skip"),
            LogisticRegression(featuresCol="features", labelCol="label", maxIter=50, regParam=0.01),
        ])
        model = pipeline.fit(train)
        predictions = model.transform(test).cache()
        predictions.count()
        evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")
        label_model = model.stages[2]
        accuracy, class_metrics = classification_metrics(predictions, label_model.labels)
        f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})
        train_counts = {row["OBJECT_TYPE"]: row["count"] for row in
                        train.groupBy("OBJECT_TYPE").count().collect()}
        test_counts = {row["OBJECT_TYPE"]: row["count"] for row in
                       test.groupBy("OBJECT_TYPE").count().collect()}
        majority_label = max(train_counts, key=train_counts.get)
        baseline = test.withColumn(
            "baseline_prediction", F.lit(majority_label)
        )
        baseline_accuracy = baseline.filter(
            F.col("OBJECT_TYPE") == F.col("baseline_prediction")
        ).count() / test.count()
        baseline_f1_values = []
        for label in sorted(set(test_counts) | {majority_label}):
            actual = baseline.filter(F.col("OBJECT_TYPE") == label).count()
            predicted = baseline.filter(F.col("baseline_prediction") == label).count()
            tp = baseline.filter((F.col("OBJECT_TYPE") == label) &
                                 (F.col("baseline_prediction") == label)).count()
            precision = tp / predicted if predicted else 0.0
            recall = tp / actual if actual else 0.0
            baseline_f1_values.append(2 * precision * recall / (precision + recall)
                                     if precision + recall else 0.0)
        model.write().overwrite().save(str(out / "model"))
        reload_model = PipelineModel.load(str(out / "model"))
        sample = test.limit(100).cache()
        original_predictions = [row["prediction"] for row in
                                model.transform(sample).select("prediction").collect()]
        reloaded_predictions = [row["prediction"] for row in
                                reload_model.transform(sample).select("prediction").collect()]
        reload_equivalent = original_predictions == reloaded_predictions
        metrics = {
            "task": "SATCAT OBJECT_TYPE classification",
            "collision_risk_model": False,
            "spark_version": spark.version,
            "pyspark_version": __import__("pyspark").__version__,
            "input": str(input_path),
            "feature_columns": FEATURES,
            "target_column": "OBJECT_TYPE",
            "rows": data.count(),
            "train_rows": train.count(),
            "test_rows": test.count(),
            "random_seed": 42,
            "accuracy": accuracy,
            "macro_f1": f1,
            "class_metrics": class_metrics,
            "overall_class_counts": {row["OBJECT_TYPE"]: row["count"] for row in
                                     data.groupBy("OBJECT_TYPE").count().collect()},
            "train_class_counts": train_counts,
            "test_class_counts": test_counts,
            "majority_class_baseline": {
                "label": majority_label,
                "accuracy": baseline_accuracy,
                "macro_f1": sum(baseline_f1_values) / len(baseline_f1_values),
            },
            "reload_prediction_equivalence": reload_equivalent,
            "preprocessing": "training-fitted median imputation, vector assembly, training-fitted label indexer",
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
