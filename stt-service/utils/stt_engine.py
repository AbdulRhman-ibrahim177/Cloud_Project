import whisper
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model (cache it to avoid reloading)
model = None

def load_whisper_model():
    """Load Whisper model on-demand"""
    global model
    if model is None:
        try:
            logger.info("Loading Whisper model (this may take a minute on first run)...")
            model = whisper.load_model("small")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            model = None
    return model

def transcribe_audio(file_bytes: bytes):
    """
    Transcribe audio bytes using Whisper
    """
    # Load model on first use
    whisper_model = load_whisper_model()
    if whisper_model is None:
        raise RuntimeError("Whisper model not loaded")
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            tmp_path = tmp.name
        
        try:
            logger.info(f"Transcribing audio from {tmp_path}")
            result = whisper_model.transcribe(tmp_path)
            text = result.get("text", "")
            logger.info(f"Transcription completed: {len(text)} characters")
            return text
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise
