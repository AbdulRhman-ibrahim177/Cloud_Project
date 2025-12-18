from fastapi import FastAPI, UploadFile, File, HTTPException
from kafka_producer import send_stt_request
import uuid
from utils.stt_engine import transcribe_audio
from utils.s3_client import upload_audio
import os
from typing import Optional

app = FastAPI(
    title="STT Service",
    version="1.0"
)

# --------------------------
# IN-MEMORY STORAGE (for testing)
# --------------------------
transcriptions_store = {}

# --------------------------
# API ROUTES
# --------------------------

@app.post("/api/stt/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Receive audio file for transcription → send event to Kafka
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Generate unique transcription ID
        transcription_id = str(uuid.uuid4())
        
        # Upload to S3
        s3_key = upload_audio(file_content, file.filename)
        
        # Store in memory
        transcriptions_store[transcription_id] = {
            "id": transcription_id,
            "filename": file.filename,
            "s3_key": s3_key,
            "text": "",
            "status": "queued",
            "content_type": file.content_type,
            "file_size": len(file_content)
        }
        
        # Send transcription request to Kafka
        event = {
            "transcription_id": transcription_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "s3_key": s3_key,
            "file_size": len(file_content)
        }
        
        send_stt_request(event)
        
        return {
            "status": "queued",
            "transcription_id": transcription_id,
            "message": "STT request queued for processing",
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.get("/api/stt/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "STT Service"
    }


@app.get("/api/stt/transcription/{tid}")
def get_transcription(tid: str):
    """
    Retrieve transcription result (later from DB)
    """
    if tid not in transcriptions_store:
        raise HTTPException(status_code=404, detail=f"Transcription {tid} not found")
    
    return transcriptions_store[tid]


@app.get("/api/stt/transcriptions")
def list_transcriptions():
    """
    List all user transcriptions
    """
    return list(transcriptions_store.values())


@app.put("/api/stt/transcription/{tid}")
def update_transcription(tid: str, text: Optional[str] = None, status: Optional[str] = None):
    """
    Update transcription result
    """
    try:
        if tid not in transcriptions_store:
            raise HTTPException(status_code=404, detail=f"Transcription {tid} not found")
        
        # Update fields
        if text is not None:
            transcriptions_store[tid]["text"] = text
        if status is not None:
            transcriptions_store[tid]["status"] = status
        
        return {
            "status": "updated",
            "transcription": transcriptions_store[tid]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating transcription: {str(e)}")


@app.delete("/api/stt/transcription/{tid}")
def delete_transcription(tid: str):
    """
    Delete transcription record
    """
    try:
        if tid not in transcriptions_store:
            raise HTTPException(status_code=404, detail=f"Transcription {tid} not found")
        
        deleted = transcriptions_store.pop(tid)
        
        return {
            "status": "deleted",
            "transcription_id": tid,
            "message": "Transcription deleted successfully"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting transcription: {str(e)}")
