"""
Quiz service API client.
"""
import requests
from django.conf import settings


class QuizServiceClient:
    """Client for Quiz service API."""
    
    def __init__(self):
        self.base_url = settings.QUIZ_SERVICE_URL
    
    def generate_quiz(self, document_id, notes, title=None, num_questions=5, 
                      difficulty='medium', question_types=None):
        """Generate a quiz from document content."""
        try:
            payload = {
                'document_id': document_id,
                'notes': notes,
                'num_questions': num_questions,
                'difficulty': difficulty,
            }
            if title:
                payload['title'] = title
            if question_types:
                payload['question_types'] = question_types
            
            response = requests.post(
                f'{self.base_url}/api/quizzes/generate',
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def get_quiz(self, quiz_id):
        """Get quiz details."""
        try:
            response = requests.get(
                f'{self.base_url}/api/quizzes/{quiz_id}',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def list_quizzes(self):
        """List all quizzes."""
        try:
            response = requests.get(
                f'{self.base_url}/api/quizzes',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'quizzes': []}
    
    def submit_quiz_response(self, quiz_id, answers):
        """Submit quiz responses."""
        try:
            response = requests.post(
                f'{self.base_url}/api/quizzes/{quiz_id}/submit',
                json={'answers': answers},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def get_quiz_results(self, quiz_id):
        """Get quiz results."""
        try:
            response = requests.get(
                f'{self.base_url}/api/quizzes/{quiz_id}/results',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


quiz_service = QuizServiceClient()
