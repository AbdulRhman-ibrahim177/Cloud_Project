from kafka import KafkaConsumer
import json
from utils.s3_client import upload_audio
from utils.stt_engine import transcribe_audio
from kafka_producer import send_stt_completed

consumer = KafkaConsumer(
    "audio.transcription.requested",
    bootstrap_servers=["localhost:39092", "localhost:39093", "localhost:39094"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("STT Worker Running...")

for msg in consumer:
    data = msg.value
    audio_bytes = bytes.fromhex(data["file_hex"])   # لو هتزودها من الAPI
    filename = data["filename"]

    # upload original file
    audio_key = upload_audio(audio_bytes, filename)

    text = transcribe_audio(audio_bytes)

    event = {
        "transcription": text,
        "filename": filename,
        "s3_key": audio_key
    }

    send_stt_completed(event)
    print("STT Completed →", event)
