from kafka import KafkaConsumer
import json

def run():
    consumer = KafkaConsumer(
        'document.uploaded',
        bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
        group_id='sample-group-python',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    print("Consumer started, waiting for messages...")

    try:
        for message in consumer:
            print(f"received | topic: {message.topic} | partition: {message.partition} | value: {message.value}")
    except KeyboardInterrupt:
        print("\nConsumer stopped manually.")
    finally:
        consumer.close()
        print("Connection closed.")

if __name__ == "__main__":
    run()
