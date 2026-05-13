from pyspark.sql import SparkSession
import os
import pyspark.sql.functions as F


input_path = "/home/aki/Documents/ad-engine/data/bronze"
output_path = "/home/aki/Documents/ad-engine/data/silver"
os.makedirs(output_path, exist_ok=True)


def salting():
    spark = SparkSession.builder \
        .appName("salting_demo") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    df = spark.read.parquet(input_path)

    SALT_BUCKETS = 10

    # Stage 1 — add random salt, aggregate on salted key
    # salt is random per row so camp_001 spreads across 10 buckets
    stage1 = df \
        .withColumn("salt", (F.rand() * SALT_BUCKETS).cast("int")) \
        .withColumn("salted_key",
            F.concat_ws("_", F.col("campaign_id"),
                            F.col("event_type"),
                            F.col("device_type"),
                            F.col("salt").cast("string"))
        ) \
        .groupBy("salted_key", "campaign_id", "event_type", "device_type") \
        .agg(
            F.count("event_id").alias("partial_events"),
            F.sum("revenue_usd").alias("partial_revenue")
        )

    # Stage 2 — remove salt, sum the partial results
    salted = stage1 \
        .groupBy("campaign_id", "event_type", "device_type") \
        .agg(
            F.sum("partial_events").alias("total_events"),
            F.round(F.sum("partial_revenue"), 4).alias("total_revenue")
        )

    salted.orderBy(F.col("total_events").desc()).show(5, truncate=False)
    
    # Write the optimized, aggregated data to the Silver layer
    salted.coalesce(1).write \
        .mode("overwrite") \
        .parquet(output_path)

    print(f"Phase 3 Complete: Silver Parquet materialized at {output_path}")
    
    spark.stop()

if __name__ == "__main__":
    salting()