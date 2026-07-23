from kafka import KafkaConsumer
from databricks.connect import DatabricksSession
import json
import os
import signal
import sys

def handle_shutdown(signum, frame):
    if batch:
        df = spark.createDataFrame(batch)
        df.write.mode("append").saveAsTable("nba_analytics.bronze.raw_player_stats")
        print(f"Wrote final {len(batch)} records to bronze table.")
    print("Stopped listening.")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# Connect to Databricks (runs Spark commands in the cloud)
spark = DatabricksSession.builder.remote(
    host=os.environ["DATABRICKS_HOST"],
    token=os.environ["DATABRICKS_TOKEN"],
    cluster_id=None,
    serverless=True
).getOrCreate()

# Connect to our local Kafka broker
consumer = KafkaConsumer(
    'nba-player-stats',
    bootstrap_servers=os.environ.get("KAFKA_BROKER", "kafka:29092"),
    auto_offset_reset='earliest',
    group_id='nba-bronze-consumer-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("Listening for messages...")

batch = []
batch_size = 100
idle_timeout_seconds = 30

while True:
    record_batch = consumer.poll(timeout_ms=idle_timeout_seconds * 1000)

    if not record_batch:
        print(f"No new messages for {idle_timeout_seconds}s. Assuming caught up.")
        break

    for tp, messages in record_batch.items():
        for message in messages:
            batch.append(message.value)

            if len(batch) >= batch_size:
                df = spark.createDataFrame(batch)
                df.write.mode("append").saveAsTable("nba_analytics.bronze.raw_player_stats")
                print(f"Wrote {len(batch)} records to bronze table.")
                batch = []

if batch:
    df = spark.createDataFrame(batch)
    df.write.mode("append").saveAsTable("nba_analytics.bronze.raw_player_stats")
    print(f"Wrote final {len(batch)} records to bronze table.")

print("Finished processing. Exiting cleanly.")