#!/usr/bin/env python3
"""
Kafka Monitor for STT Service
Monitors Kafka topics and displays messages in real-time
"""
import json
from kafka import KafkaConsumer
import threading
import time
from datetime import datetime

# Kafka configuration
KAFKA_BROKERS = ['localhost:39092', 'localhost:39093', 'localhost:39094']
TOPICS = [
    'audio.transcription.requested',
    'audio.transcription.completed'
]

class KafkaMonitor:
    def __init__(self, topics):
        self.topics = topics
        self.running = True
        self.message_count = {topic: 0 for topic in topics}
        
    def start(self):
        """Start monitoring Kafka topics"""
        print("=" * 80)
        print("🔍 KAFKA MONITOR FOR STT SERVICE")
        print("=" * 80)
        print(f"📍 Brokers: {', '.join(KAFKA_BROKERS)}")
        print(f"📌 Topics: {', '.join(self.topics)}")
        print(f"⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("\n⏳ Waiting for messages... (Press CTRL+C to stop)\n")
        
        try:
            consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=KAFKA_BROKERS,
                auto_offset_reset='latest',  # Only show new messages
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                group_id='stt-monitor-group',
                consumer_timeout_ms=5000
            )
            
            print("✅ Connected to Kafka\n")
            
            while self.running:
                try:
                    for message in consumer:
                        self.message_count[message.topic] += 1
                        self.print_message(message)
                except StopIteration:
                    # No more messages available
                    pass
                    
        except Exception as e:
            print(f"❌ Error connecting to Kafka: {e}")
            print("\n⚠️  Make sure Kafka is running:")
            print("   cd C:\\Users\\bedya\\OneDrive\\Documents\\GitHub\\Cloud_Project\\kafka")
            print("   docker-compose up -d")
            
    def print_message(self, message):
        """Pretty print a Kafka message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        topic = message.topic
        
        if topic == 'audio.transcription.requested':
            emoji = "📤"
            status = "REQUEST RECEIVED"
        else:
            emoji = "✅"
            status = "COMPLETED"
            
        print(f"{emoji} [{timestamp}] {status}")
        print(f"   Topic: {topic}")
        print(f"   Message: {json.dumps(message.value, indent=2)}")
        print()

def display_menu():
    """Display monitoring options"""
    print("\n" + "=" * 80)
    print("🎯 KAFKA MONITORING OPTIONS")
    print("=" * 80)
    print("\n1️⃣  Start Real-Time Monitor (This Script)")
    print("   python monitor_kafka.py\n")
    print("2️⃣  View Topic Details")
    print("   docker exec kafka-1 kafka-topics --list --bootstrap-server kafka-1:29092\n")
    print("3️⃣  Monitor Single Topic (Command Line)")
    print("   docker exec kafka-1 kafka-console-consumer \\")
    print("     --topic audio.transcription.requested \\")
    print("     --bootstrap-server kafka-1:29092 \\")
    print("     --from-beginning\n")
    print("4️⃣  Monitor with Kafdrop (Web UI)")
    print("   Open: http://localhost:39000\n")
    print("=" * 80)

if __name__ == "__main__":
    monitor = KafkaMonitor(TOPICS)
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("📊 KAFKA MONITOR SUMMARY")
        print("=" * 80)
        for topic, count in monitor.message_count.items():
            print(f"   {topic}: {count} messages")
        print("=" * 80)
        print("✋ Monitor stopped\n")
        display_menu()
