from kafka import KafkaConsumer
import json
import os
from utils.s3_client import upload_audio
from utils.stt_engine import transcribe_audio
from kafka_producer import send_stt_completed

# Get Kafka brokers from environment or use defaults
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:39092,localhost:39093,localhost:39094').split(',')

consumer = KafkaConsumer(
    "audio.transcription.requested",
    bootstrap_servers=KAFKA_BROKERS,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    group_id="stt-service-group",
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

print("STT Worker Running...")
print(f"Connected to Kafka brokers: {KAFKA_BROKERS}")

for msg in consumer:
    try:
        data = msg.value
        print(f"Received message: {data}")
        
        # Get file from S3 key or from hex-encoded data
        if "file_hex" in data:
            audio_bytes = bytes.fromhex(data["file_hex"])
        elif "s3_key" in data:
            # In production, download from S3
            print(f"Processing file from S3: {data['s3_key']}")
            continue
        else:
            print("Warning: No audio data found in message")
            continue
            
        filename = data.get("filename", "unknown")
        
        # Transcribe audio
        print(f"Transcribing audio: {filename}")
        text = transcribe_audio(audio_bytes)
        
        # Prepare completion event
        event = {
            "transcription_id": data.get("transcription_id"),
            "transcription": text,
            "filename": filename,
            "s3_key": data.get("s3_key", "")
        }
        
        # Send completion event to Kafka
        send_stt_completed(event)
        print(f"STT Completed → {event}")
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
