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

    try:
        future = producer.send(
            TOPIC,
            key=user_id.encode("utf-8"),   # 👈 مهم جدًا
            value=payload
        )
        record_metadata = future.get(timeout=10)
        print(
            f"[INFO] Message sent | "
            f"topic={record_metadata.topic}, "
            f"partition={record_metadata.partition}, "
            f"offset={record_metadata.offset}"
        )
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}", file=sys.stderr)