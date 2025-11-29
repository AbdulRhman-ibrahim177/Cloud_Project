from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
import sys


def run():
    producer = None

    try:
        # إنشاء الـ Producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except KafkaError as e:
        print(f"[ERROR] Failed to create KafkaProducer: {e}", file=sys.stderr)
        return
    except Exception as e:
        print(f"[ERROR] Unexpected error while creating producer: {e}", file=sys.stderr)
        return

    # الرسالة التجريبية
    message = {
        'id': 'doc1',
        'name': 'file.pdf',
        'userId': 10,
        'time': int(time.time() * 1000)  # نفس Date.now() في JavaScript
    }

    try:
        future = producer.send('document.uploaded', value=message)

        # ننتظر نتيجة الإرسال عشان نكشف أي error من Kafka
        record_metadata = future.get(timeout=10)
        print(
            f"[INFO] Message sent successfully "
            f"(topic={record_metadata.topic}, partition={record_metadata.partition}, offset={record_metadata.offset})"
        )

    except KafkaError as e:
        print(f"[ERROR] Failed to send message to Kafka: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Unexpected error while sending message: {e}", file=sys.stderr)
    finally:
        if producer is not None:
            try:
                producer.flush()
                producer.close()
            except Exception as e:
                print(f"[WARN] Error while closing producer: {e}", file=sys.stderr)


if __name__ == "__main__":
    run()
