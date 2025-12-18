# stt-service/kafka_producer.py
from kafka import KafkaProducer
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Kafka brokers from environment or use defaults
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:39092,localhost:39093,localhost:39094').split(',')

producer = None

def get_producer():
    """Get or create Kafka producer with error handling"""
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                request_timeout_ms=5000
            )
            logger.info("Kafka producer initialized")
        except Exception as e:
            logger.warning(f"Kafka producer init delayed: {e}")
            producer = None
    return producer

def send_stt_request(event):
    """Send STT transcription request to Kafka"""
    prod = get_producer()
    if prod:
        try:
            prod.send("audio.transcription.requested", event)
            prod.flush()
            logger.info(f"Sent STT request: {event.get('id')}")
        except Exception as e:
            logger.error(f"Failed to send STT request: {e}")
    else:
        logger.warning("Kafka producer unavailable, skipping message")

def send_stt_completed(event):
    """Send STT transcription completion to Kafka"""
    prod = get_producer()
    if prod:
        try:
            prod.send("audio.transcription.completed", event)
            prod.flush()
            logger.info(f"Sent STT completed: {event.get('id')}")
        except Exception as e:
            logger.error(f"Failed to send STT completed: {e}")
    else:
        logger.warning("Kafka producer unavailable, skipping message")
