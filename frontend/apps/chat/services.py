"""
Chat service API client.
"""
import requests
from django.conf import settings


class ChatServiceClient:
    """Client for chat service API."""
    
    def __init__(self):
        self.base_url = settings.CHAT_SERVICE_URL
    
    def send_message(self, user_id, message):
        """Send message to chat service."""
        try:
            response = requests.post(
                f'{self.base_url}/message',
                json={
                    'user_id': user_id,
                    'message': message,
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}


chat_service = ChatServiceClient()
