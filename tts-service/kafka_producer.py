# tts-service/kafka_producer.py
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_tts_completed(event):
    producer.send("audio.generation.completed", event)
    producer.flush()
