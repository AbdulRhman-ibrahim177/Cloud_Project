import whisper
import tempfile

model = whisper.load_model("small")

def transcribe_audio(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        result = model.transcribe(tmp.name)
        return result["text"]
