import json
from kafka import KafkaProducer
import time
import sys

BOOTSTRAP_SERVERS = ["localhost:39092", "localhost:39093", "localhost:39094"]
TOPIC = "chat.message"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    key_serializer=lambda k: k,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def produce_chat_message(user_id: str, message: str):
    payload = {
        "user_id": user_id,
        "message": message,
        "timestamp": int(time.time() * 1000)
    }

    producer.send(
        TOPIC,
        key=str(user_id).encode(),
        value=payload
    )

    producer.flush()