from kafka import KafkaConsumer
import json
from utils.tts_engine import synthesize_speech
from utils.s3_client import upload_file
from kafka_producer import send_tts_completed

consumer = KafkaConsumer(
    "audio.generation.requested",
    bootstrap_servers=["localhost:39092", "localhost:39093", "localhost:39094"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("TTS Worker Running...")

for msg in consumer:
    data = msg.value
    text = data["text"]
    lang = data.get("language", "en")

    audio_bytes = synthesize_speech(text, lang)
    file_id, key = upload_file(audio_bytes)

    event = {
        "audio_id": file_id,
        "s3_key": key
    }

    send_tts_completed(event)
    print("TTS Completed →", event)
