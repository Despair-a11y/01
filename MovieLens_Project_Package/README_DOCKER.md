# Docker Environment Guide

This guide explains how to set up and run the MovieLens Spark & HBase experiment using Docker.

## 1. Prerequisites

- Docker installed
- Docker Compose installed

## 2. Start the Environment

Run the following command to build images and start services:

```bash
docker-compose up -d --build
```

This will start:
- **HBase**: http://localhost:16010
- **Spark Master**: http://localhost:8080
- **Spark Worker**: (Connected to Master)

## 3. Run Spark Batch Processing (Experiment 1)

This job calculates movie ratings from CSV and saves them to HBase.

```bash
docker-compose exec spark-master spark-submit /app/spark_batch.py
```

## 4. Run Spark Streaming (Experiment 2)

This requires two terminals.

**Terminal 1: Start the Data Producer**
(Run this on your host machine or inside a container)
```bash
python3 stream_producer.py
```

**Terminal 2: Submit Spark Streaming Job**
```bash
docker-compose exec spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /app/spark_streaming.py
```
*(Note: If the socket connection fails, ensure `stream_producer.py` is running and accessible via `host.docker.internal`)*

## 5. Stop the Environment

```bash
docker-compose down
```
