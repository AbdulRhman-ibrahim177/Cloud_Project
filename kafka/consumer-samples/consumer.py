from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import sys


def run():
    consumer = None

    # إنشاء الـ Consumer
    try:
        consumer = KafkaConsumer(
            'document.uploaded',
            bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
            group_id='sample-group-python',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
    except KafkaError as e:
        print(f"[ERROR] Failed to create KafkaConsumer: {e}", file=sys.stderr)
        return
    except Exception as e:
        print(f"[ERROR] Unexpected error while creating consumer: {e}", file=sys.stderr)
        return

    print("Consumer started, waiting for messages...")

    try:
        for message in consumer:
            try:
                print(
                    f"received | topic: {message.topic} | "
                    f"partition: {message.partition} | value: {message.value}"
                )
            except Exception as e:
                # خطأ في معالجة رسالة واحدة ما يوقفش الـ consumer كله
                print(f"[WARN] Error while handling message: {e}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nConsumer stopped manually.")
    except KafkaError as e:
        print(f"[ERROR] Kafka error in consumer loop: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Unexpected error in consumer loop: {e}", file=sys.stderr)
    finally:
        if consumer is not None:
            try:
                consumer.close()
                print("Connection closed.")
            except Exception as e:
                print(f"[WARN] Error while closing consumer: {e}", file=sys.stderr)


if __name__ == "__main__":
    run()
