import json
from kafka import KafkaConsumer
import threading
import sys

# استخدم البورتات الخارجية عشان تتصل من Windows
BOOTSTRAP_SERVERS = ["localhost:39092", "localhost:39093", "localhost:39094"]
TOPIC = "chat.message"

def start_consumer():
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
    except Exception as e:
        print(f"[ERROR] Failed to create KafkaConsumer: {e}", file=sys.stderr)
        return

    print("Kafka Consumer started, waiting for messages...")
    try:
        for msg in consumer:
            print(f"Received message: {msg.value}")
    except Exception as e:
        print(f"[ERROR] Consumer stopped: {e}")
    finally:
        consumer.close()

def start_consumer_in_thread():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()