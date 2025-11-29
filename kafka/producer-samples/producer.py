
from kafka import KafkaProducer
import json
import time

def run():
    # إنشاء المنتج (Producer)
    producer = KafkaProducer(
        bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # تحويل البيانات لـ JSON
    )

    # إرسال الرسالة
    message = {
        'id': 'doc1',
        'name': 'file.pdf',
        'userId': 10,
        'time': int(time.time() * 1000)  # نفس Date.now() في JavaScript
    }

    producer.send('document.uploaded', value=message)
    producer.flush()  # تأكيد الإرسال
    print('sent')

    producer.close()

if __name__ == "__main__":
    run()

