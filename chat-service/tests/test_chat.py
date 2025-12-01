import time
import json
from fastapi.testclient import TestClient
from kafka import KafkaConsumer
from main import app

client = TestClient(app)

BOOTSTRAP = ["localhost:39092", "localhost:39093", "localhost:39094"]
TOPIC = "chat.message"


def test_chat_message_real_kafka():

    # Step 1: ابعت request للـ API
    payload = {
        "user_id": "user123",
        "message": "Hello Kafka"
    }

    response = client.post("/api/chat/message", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == "user123"
    assert data["message"] == "Hello Kafka"
    assert "response" in data

    # Step 2: افتح Kafka Consumer حقيقي يشوف الرسالة وصلت ولا لأ
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset='latest',   # أحدث رسالة
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    found = False
    timeout = time.time() + 10   # ندي Kafka فرصة 10 ثواني

    while time.time() < timeout:
        for msg in consumer:
            value = msg.value
            print("Received from Kafka:", value)

            if value["user_id"] == "user123" and value["message"] == "Hello Kafka":
                found = True
                break
        if found:
            break

    consumer.close()

    assert found, "Message NOT found in Kafka topic chat.message"