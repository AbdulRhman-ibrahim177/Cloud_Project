from fastapi import FastAPI, UploadFile, File
from kafka_producer import send_stt_completed

app = FastAPI(
    title="STT Service",
    version="1.0"
)

# --------------------------
# API ROUTES
# --------------------------

@app.post("/api/stt/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Receive audio file for transcription → send event to Kafka
    """
    event = {
        "transcription_id": "tr_" + file.filename[:5],
        "filename": file.filename,
        "content_type": file.content_type
    }

    send_stt_completed(event)

    return {
        "status": "queued",
        "message": "STT request sent to Kafka",
        "event": event
    }


@app.get("/api/stt/transcription/{tid}")
def get_transcription(tid: str):
    """
    Retrieve transcription result (later from DB)
    """
    return {
        "id": tid,
        "text": "sample transcription (placeholder)"
    }


@app.get("/api/stt/transcriptions")
def list_transcriptions():
    """
    List all user transcriptions (later from DB)
    """
    return [
        {"id": "1", "text": "hello world"},
        {"id": "2", "text": "speech to text example"}
    ]
from fastapi import FastAPI, UploadFile, File
from kafka_producer import send_stt_completed

app = FastAPI(
    title="STT Service",
    version="1.0"
)

# --------------------------
# API ROUTES
# --------------------------

@app.post("/api/stt/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Receive audio file for transcription → send event to Kafka
    """
    event = {
        "transcription_id": "tr_" + file.filename[:5],
        "filename": file.filename,
        "content_type": file.content_type
    }

    send_stt_completed(event)

    return {
        "status": "queued",
        "message": "STT request sent to Kafka",
        "event": event
    }


@app.get("/api/stt/transcription/{tid}")
def get_transcription(tid: str):
    """
    Retrieve transcription result (later from DB)
    """
    return {
        "id": tid,
        "text": "sample transcription (placeholder)"
    }


@app.get("/api/stt/transcriptions")
def list_transcriptions():
    """
    List all user transcriptions (later from DB)
    """
    return [
        {"id": "1", "text": "hello world"},
        {"id": "2", "text": "speech to text example"}
    ]
