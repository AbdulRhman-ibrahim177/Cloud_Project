"""
STT service API client.
"""
import requests
from django.conf import settings


class STTServiceClient:
    """Client for Speech-to-Text service API."""
    
    def __init__(self):
        self.base_url = settings.STT_SERVICE_URL
    
    def transcribe_audio(self, file_obj):
        """Upload audio file for transcription."""
        try:
            files = {'file': file_obj}
            response = requests.post(
                f'{self.base_url}/api/stt/transcribe',
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def get_transcription(self, transcription_id):
        """Get transcription result."""
        try:
            response = requests.get(
                f'{self.base_url}/api/stt/transcription/{transcription_id}',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'text': ''}
    
    def list_transcriptions(self):
        """List all transcriptions."""
        try:
            response = requests.get(
                f'{self.base_url}/api/stt/transcriptions',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'transcriptions': []}
    
    def health_check(self):
        """Check service health."""
        try:
            response = requests.get(
                f'{self.base_url}/api/stt/health',
                timeout=5
            )
            response.raise_for_status()
            return {'status': 'healthy'}
        except requests.exceptions.RequestException:
            return {'status': 'unhealthy'}


stt_service = STTServiceClient()
