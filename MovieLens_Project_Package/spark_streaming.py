"""
Spark Streaming Script
Goal: Calculate real-time popular movies (top 10 in last 10 minutes).
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, count, desc
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import sys

def main():
    spark = SparkSession.builder \
        .appName("MovieLensRealTime") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Define schema for incoming JSON data
    schema = StructType([
        StructField("userId", IntegerType()),
        StructField("movieId", IntegerType()),
        StructField("rating", DoubleType()),
        StructField("timestamp", TimestampType())
    ])

    # Read from socket
    # Note: In production this would be Kafka
    lines = spark.readStream \
        .format("socket") \
        .option("host", "host.docker.internal") \
        .option("port", 9999) \
        .load()

    # Parse JSON
    ratings = lines.select(from_json(col("value"), schema).alias("data")).select("data.*")

    # Filter out nulls
    ratings = ratings.filter(col("movieId").isNotNull())

    # Windowed aggregation: Top movies in last 10 minutes, updating every 1 minute
    windowed_counts = ratings \
        .groupBy(
            window(col("timestamp"), "10 minutes", "1 minute"),
            col("movieId")
        ) \
        .count()

    # Sort by count desc
    query = windowed_counts \
        .orderBy(desc("window"), desc("count")) \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 20) \
        .start()

    print("="*50)
    print("Spark Streaming Job Started")
    print("Listening on host.docker.internal:9999")
    print("="*50)

    query.awaitTermination()

if __name__ == "__main__":
    main()
