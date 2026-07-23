from nba_api.stats.endpoints import leaguegamelog
from kafka import KafkaProducer
import json
import time
import os

# Connect to our local Kafka broker
producer = KafkaProducer(
    bootstrap_servers=os.environ.get("KAFKA_BROKER", "kafka:29092"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Pull historical game log data for the 2023-24 season
print("Fetching game log data...")
game_log = leaguegamelog.LeagueGameLog(season='2023-24')
games_df = game_log.get_data_frames()[0]

print(f"Retrieved {len(games_df)} rows. Sending to Kafka...")

# Send each row as a separate message to the topic
for index, row in games_df.iterrows():
    record = row.to_dict()
    producer.send('nba-player-stats', value=record)
    if index % 100 == 0:
        print(f"Sent {index} records...")
    time.sleep(0.01)  # small delay so we're not blasting Kafka instantly

producer.flush()
print("Done sending all records.")