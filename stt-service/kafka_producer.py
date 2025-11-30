# stt-service/kafka_producer.py
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_stt_completed(event):
    producer.send("audio.transcription.completed", event)
    producer.flush()
