"""
TTS service API client.
"""
import requests
from django.conf import settings


class TTSServiceClient:
    """Client for Text-to-Speech service API."""
    
    def __init__(self):
        self.base_url = settings.TTS_SERVICE_URL
    
    def synthesize_text(self, text, voice='default'):
        """Send text to be synthesized to speech."""
        try:
            response = requests.post(
                f'{self.base_url}/api/tts/synthesize',
                json={
                    'text': text,
                    'voice': voice,
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def get_synthesis(self, synthesis_id):
        """Get synthesis result."""
        try:
            response = requests.get(
                f'{self.base_url}/api/tts/synthesis/{synthesis_id}',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'audio_url': ''}
    
    def list_syntheses(self):
        """List all syntheses."""
        try:
            response = requests.get(
                f'{self.base_url}/api/tts/syntheses',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'syntheses': []}
    
    def get_voices(self):
        """Get available voices."""
        try:
            response = requests.get(
                f'{self.base_url}/api/tts/voices',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'voices': []}


tts_service = TTSServiceClient()
