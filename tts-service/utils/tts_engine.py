from gtts import gTTS
from io import BytesIO

def synthesize_speech(text: str, lang="en"):
    tts = gTTS(text=text, lang=lang)
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()
