import sys
import boto3
import json
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder.appName('reddit_json_to_csv').getOrCreate()

source_s3_path = "s3://project-reddit-etl/raw/reddit_posts.json"
target_s3_path = "s3://project-reddit-etl/processed/reddit_posts.csv"

try:
    # Read the JSON file from S3
    df = spark.read.json(source_s3_path)
    
    # Save as Parquet file
    df.write.mode("overwrite").csv(target_s3_path)
    print(f"Successfully read JSON file from {source_s3_path} and saved as CSV file into {target_s3_path}")
except Exception as e:
    print(f"Error: {e}")
finally:
    spark.stop()