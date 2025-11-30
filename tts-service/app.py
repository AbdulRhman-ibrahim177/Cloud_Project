from fastapi import FastAPI
from pydantic import BaseModel
from kafka_producer import send_tts_completed

app = FastAPI(
    title="TTS Service",
    version="1.0"
)

# --------------------------
# Request Model
# --------------------------
class TTSRequest(BaseModel):
    text: str
    language: str = "en"

# --------------------------
# API Routes
# --------------------------

@app.post("/api/tts/synthesize")
def synthesize(request: TTSRequest):
    """
    Receive TTS request from client → publish event to Kafka topic
    """
    event = {
        "audio_id": "audio_" + request.text[:5],  # temporary ID
        "text": request.text,
        "language": request.language,
    }

    send_tts_completed(event)

    return {
        "status": "queued",
        "message": "TTS request sent to Kafka",
        "event": event
    }


@app.get("/api/tts/audio/{audio_id}")
def get_audio(audio_id: str):
    """
    Fetch audio file metadata (later you link S3)
    """
    return {
        "audio_id": audio_id,
        "url": f"https://dummy-s3/tts/{audio_id}.mp3"
    }


@app.delete("/api/tts/audio/{audio_id}")
def delete_audio(audio_id: str):
    """
    Delete audio file (implement S3 delete later)
    """
    return {
        "status": "deleted",
        "audio_id": audio_id
    }
