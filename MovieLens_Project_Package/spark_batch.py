"""
Spark Batch Processing Script
Goal: Calculate average ratings for each movie and update HBase.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count
import happybase
import os

# HBase Configuration
HBASE_HOST = 'hbase'
HBASE_PORT = 9090


def get_hbase_connection():
    """Get HBase connection"""
    try:
        connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT)
        return connection
    except Exception as e:
        print(f"Failed to connect to HBase: {e}")
        return None

def write_to_hbase(row):
    """Write a single row to HBase (used in foreach)"""
    # Note: Creating connection inside foreach is inefficient for large scale, 
    # but acceptable for this small dataset/demo. 
    # For production, use mapPartitions.
    try:
        connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT)
        table = connection.table('movies')
        
        movie_id = str(row['movieId']).encode()
        
        # Update rating info
        data = {
            b'info:avg_rating': str(round(row['avg_rating'], 2)).encode(),
            b'info:rating_count': str(row['count']).encode()
        }
        
        table.put(movie_id, data)
        connection.close()
    except Exception as e:
        print(f"Error writing to HBase: {e}")

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("MovieLensBatchProcessing") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print("="*50)
    print("Starting Spark Batch Processing")
    print("="*50)

    # Define paths (mapped volume in Docker)
    movies_path = "/app/ml-latest-small/movies.csv"
    ratings_path = "/app/ml-latest-small/ratings.csv"

    # Read Data
    print(f"Reading movies from {movies_path}")
    movies_df = spark.read.csv(movies_path, header=True, inferSchema=True)
    
    print(f"Reading ratings from {ratings_path}")
    ratings_df = spark.read.csv(ratings_path, header=True, inferSchema=True)

    # Calculate Average Ratings
    print("Calculating average ratings...")
    movie_ratings = ratings_df.groupBy("movieId").agg(
        avg("rating").alias("avg_rating"),
        count("rating").alias("count")
    )

    # Join with movie titles for display
    result_df = movie_ratings.join(movies_df, "movieId")
    
    # Show top 10 rated movies (with > 50 ratings)
    print("\nTop 10 Rated Movies (with > 50 ratings):")
    result_df.filter("count > 50") \
             .orderBy(col("avg_rating").desc()) \
             .select("title", "avg_rating", "count") \
             .show(10, truncate=False)

    # Write to HBase
    print("\nWriting results to HBase...")
    # Collect to driver for simple writing (since dataset is small)
    # For large datasets, use rdd.foreachPartition
    results = result_df.collect()
    
    connection = get_hbase_connection()
    if connection:
        table = connection.table('movies')
        batch = table.batch(batch_size=1000)
        
        processed_count = 0
        for row in results:
            movie_id = str(row['movieId']).encode()
            data = {
                b'info:avg_rating': str(round(row['avg_rating'], 2)).encode(),
                b'info:rating_count': str(row['count']).encode()
            }
            batch.put(movie_id, data)
            processed_count += 1
            
        batch.send()
        connection.close()
        print(f"Successfully updated {processed_count} movies in HBase")
    else:
        print("Skipping HBase write due to connection error")

    spark.stop()
    print("="*50)
    print("Batch Processing Completed")
    print("="*50)

if __name__ == "__main__":
    main()
