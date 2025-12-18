"""
Document service API client.
"""
import requests
from django.conf import settings


class DocumentServiceClient:
    """Client for document service API."""
    
    def __init__(self):
        self.base_url = settings.DOCUMENT_SERVICE_URL
    
    def upload_document(self, file_obj):
        """Upload document file."""
        try:
            files = {'file': file_obj}
            response = requests.post(
                f'{self.base_url}/api/documents/upload',
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def get_documents(self, user_id=None):
        """Get list of documents."""
        try:
            params = {'user_id': user_id} if user_id else {}
            response = requests.get(
                f'{self.base_url}/api/documents',
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'documents': []}
    
    def get_document_notes(self, document_id):
        """Get generated notes for a document."""
        try:
            response = requests.get(
                f'{self.base_url}/api/documents/{document_id}/notes',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'notes': ''}
    
    def delete_document(self, document_id):
        """Delete a document."""
        try:
            response = requests.delete(
                f'{self.base_url}/api/documents/{document_id}',
                timeout=10
            )
            response.raise_for_status()
            return {'status': 'deleted'}
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}


document_service = DocumentServiceClient()
