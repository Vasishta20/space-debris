"""Optional unsupervised MLlib exploratory ranking; not collision-risk prediction."""
import argparse
import json
import math
from pathlib import Path


FEATURES = ("distance_km", "relative_velocity_km_s")


def validate_candidates(rows):
    errors = []
    for index, row in enumerate(rows):
        for field in FEATURES:
            if field not in row:
                errors.append(f"row {index}: missing {field}")
            else:
                try: value = float(row[field])
                except (TypeError, ValueError): errors.append(f"row {index}: invalid {field}"); continue
                if not math.isfinite(value) or value < 0: errors.append(f"row {index}: non-finite/negative {field}")
        if row.get("distance_units", "km") != "km": errors.append(f"row {index}: distance_units must be km")
        if row.get("velocity_units", "km/s") != "km/s": errors.append(f"row {index}: velocity_units must be km/s")
    return errors


def fit_exploratory_mllib(rows, output_path):
    """Fit an unsupervised physical-feature clustering model in Spark.

    The returned ordering is similarity to the nearest learned cluster, not
    collision likelihood. This function is deliberately unreachable for the
    current one-row input through ``run``.
    """
    from pyspark.sql import SparkSession, functions as F
    from pyspark.ml import Pipeline
    from pyspark.ml.clustering import KMeans
    from pyspark.ml.feature import StandardScaler, VectorAssembler

    spark = SparkSession.builder.master("local[2]").appName("exploratory-conjunction-ranking").getOrCreate()
    try:
        frame = spark.createDataFrame([(float(row[FEATURES[0]]), float(row[FEATURES[1]])) for row in rows], FEATURES)
        assembler = VectorAssembler(inputCols=list(FEATURES), outputCol="raw_features")
        scaler = StandardScaler(inputCol="raw_features", outputCol="features", withMean=True, withStd=True)
        kmeans = KMeans(featuresCol="features", predictionCol="cluster_id", k=min(3, len(rows)), seed=42)
        model = Pipeline(stages=[assembler, scaler, kmeans]).fit(frame)
        transformed = model.transform(frame)
        centers = model.stages[-1].clusterCenters()

        def distance_to_center(vector, center):
            return float(sum((float(left) - float(right)) ** 2 for left, right in zip(vector, center)) ** 0.5)

        distance_udf = F.udf(lambda vector, cluster: distance_to_center(vector, centers[int(cluster)]), "double")
        ranked = transformed.withColumn("cluster_distance", distance_udf(F.col("features"), F.col("cluster_id"))) \
                            .orderBy(F.col("cluster_distance").asc())
        result = [row.asDict() for row in ranked.select(*FEATURES, "cluster_id", "cluster_distance").collect()]
        Path(output_path).write_text(json.dumps({"status": "fit", "algorithm": "StandardScaler + KMeans",
            "rows": len(rows), "ranking": result, "not_a_collision_probability": True,
            "interpretation": "ascending distance to learned feature cluster; exploratory similarity only"}, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        spark.stop()


def run(input_path, output_path, min_candidates=3):
    source = json.loads(Path(input_path).read_text(encoding="utf-8"))
    rows = source if isinstance(source, list) else source.get("candidates", [])
    errors = validate_candidates(rows)
    result = {"method": "unsupervised Spark MLlib exploratory clustering", "not_a_collision_probability": True,
              "not_a_supervised_collision_model": True, "input_rows": len(rows), "validation_errors": errors}
    if errors:
        result["status"] = "invalid_input"
    elif len(rows) < min_candidates:
        result["status"] = "not_ready_for_fit"
        result["reason"] = f"at least {min_candidates} independent candidates are required; no rows were duplicated"
    else:
        result["status"] = "fit_required_in_wsl"
        result["algorithm"] = "StandardScaler + KMeans; cluster proximity is exploratory structure, not risk"
    Path(output_path).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("input"); parser.add_argument("output")
    args = parser.parse_args(); run(args.input, args.output)
