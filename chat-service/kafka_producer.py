import json
from kafka import KafkaProducer
import time
import sys

# استخدم البورتات الخارجية عشان تتصل من Windows
BOOTSTRAP_SERVERS = ["localhost:39092", "localhost:39093", "localhost:39094"]
TOPIC = "chat.message"

try:
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception as e:
    print(f"[ERROR] Failed to create KafkaProducer: {e}", file=sys.stderr)
    sys.exit(1)


def produce_chat_message(user_id: str, message: str):
    payload = {
        "user_id": user_id,
        "message": message,
        "timestamp": int(time.time() * 1000)
    }
    try:
        future = producer.send(TOPIC, value=payload)
        record_metadata = future.get(timeout=10)
        print(f"[INFO] Message sent | topic={record_metadata.topic}, partition={record_metadata.partition}, offset={record_metadata.offset}")
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}", file=sys.stderr)