"""Bounded WSL2 PySpark worker smoke test.

This intentionally uses only eight in-memory records and does not read the
joined dataset or any D: drive path.
"""

import os
import subprocess
import sys

from pyspark.sql import SparkSession


def main() -> None:
    expected = [2, 4, 6, 8, 10, 12, 14, 16]
    print(f"python_executable={sys.executable}")
    print(f"python_version={sys.version.split()[0]}")
    print(f"pyspark_version={__import__('pyspark').__version__}")
    java = subprocess.run(["java", "-version"], capture_output=True, text=True)
    print("java_version=" + (java.stderr or java.stdout).splitlines()[0])

    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("space-debris-wsl-smoke")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    try:
        sc = spark.sparkContext
        print(f"spark_version={spark.version}")
        print(f"master={sc.master}")
        print(f"default_parallelism={sc.defaultParallelism}")

        values = sc.parallelize(range(1, 9), 2).map(lambda value: value * 2)
        actual = values.collect()
        worker_info = values.mapPartitions(
            lambda iterator: [(sys.executable, sys.version.split()[0])]
        ).collect()
        print(f"result={actual}")
        print(f"expected={expected}")
        print(f"worker_info={worker_info}")
        print(f"partitions={values.getNumPartitions()}")
        if actual != expected or not worker_info:
            raise AssertionError("PySpark worker result did not match expected output")
        print("smoke_status=PASS")
    finally:
        spark.stop()
        print("spark_stopped=true")


if __name__ == "__main__":
    main()
