from pyspark.sql import SparkSession
import os

input_path = "/home/aki/Documents/ad-engine/data/raw"
output_path = "/home/aki/Documents/ad-engine/data/bronze"
os.makedirs(output_path, exist_ok=True)

def raw2bronze():
    spark = SparkSession.builder.appName("raw2bronze").getOrCreate()
    df = spark.read.json(input_path+"/*.json")
    df.write.mode("overwrite").parquet(output_path)
    spark.stop()

if __name__ == "__main__":
    raw2bronze()


