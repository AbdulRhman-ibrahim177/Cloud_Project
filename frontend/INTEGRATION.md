# Integration Guide - Cloud Project Frontend

This guide explains how the Django frontend integrates with the backend microservices.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                 Django Frontend (8000)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Views | Templates | Static Files | API Clients │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
              ↓      ↓      ↓      ↓      ↓
     ┌────────┴──┬───┴──┬────┴──┬───┴──┬───┴────┐
     │            │      │       │      │        │
  Chat(8001)  Doc(8002) STT(8003) TTS(8004) Quiz(8005)
```

## Service Integration

### 1. Chat Service (Port 8001)

**Frontend Files:**
- [apps/chat/services.py](apps/chat/services.py) - API client
- [apps/chat/views.py](apps/chat/views.py) - Views
- [templates/chat/chat.html](templates/chat/chat.html) - Interface

**API Endpoint Used:**
```
POST /message
{
    "user_id": "user_id",
    "message": "user message"
}
```

**Response:**
```json
{
    "user_id": "user_id",
    "message": "user message",
    "response": "ai response"
}
```

### 2. Document Service (Port 8002)

**Frontend Files:**
- [apps/documents/services.py](apps/documents/services.py) - API client
- [apps/documents/views.py](apps/documents/views.py) - Views
- [templates/documents/](templates/documents/) - Interfaces

**API Endpoints Used:**
```
POST /api/documents/upload - Upload document
GET /api/documents - List documents
GET /api/documents/{id}/notes - Get generated notes
DELETE /api/documents/{id} - Delete document
```

### 3. STT Service (Port 8003)

**Frontend Files:**
- [apps/stt/services.py](apps/stt/services.py) - API client
- [apps/stt/views.py](apps/stt/views.py) - Views
- [templates/stt/stt.html](templates/stt/stt.html) - Interface

**API Endpoints Used:**
```
POST /api/stt/transcribe - Upload audio
GET /api/stt/transcription/{id} - Get transcription
GET /api/stt/transcriptions - List all
GET /api/stt/health - Health check
```

### 4. TTS Service (Port 8004)

**Frontend Files:**
- [apps/tts/services.py](apps/tts/services.py) - API client
- [apps/tts/views.py](apps/tts/views.py) - Views
- [templates/tts/tts.html](templates/tts/tts.html) - Interface

**API Endpoints Used:**
```
POST /api/tts/synthesize - Convert text to speech
GET /api/tts/synthesis/{id} - Get synthesis result
GET /api/tts/voices - Get available voices
```

### 5. Quiz Service (Port 8005)

**Frontend Files:**
- [apps/quiz/services.py](apps/quiz/services.py) - API client
- [apps/quiz/views.py](apps/quiz/views.py) - Views
- [templates/quiz/](templates/quiz/) - Interfaces

**API Endpoints Used:**
```
POST /api/quizzes/generate - Generate quiz
GET /api/quizzes - List quizzes
GET /api/quizzes/{id} - Get quiz
POST /api/quizzes/{id}/submit - Submit answers
GET /api/quizzes/{id}/results - Get results
```

## Data Flow Examples

### Example 1: Chat Flow
```
User Input (Frontend) 
    ↓
JavaScript sends POST to /chat/api/send/
    ↓
Django view calls chat_service.send_message()
    ↓
Service client makes HTTP request to Chat Service
    ↓
Chat Service processes and responds
    ↓
Response displayed in chat box (JavaScript)
```

### Example 2: Document Upload Flow
```
User selects file (Frontend)
    ↓
JavaScript FormData to /documents/api/upload/
    ↓
Django view saves to models
    ↓
Service client makes multipart request to Document Service
    ↓
Document Service processes and generates notes
    ↓
Frontend redirects to document details
    ↓
Notes fetched and displayed
```

### Example 3: Quiz Generation Flow
```
User enters document content (Frontend)
    ↓
JavaScript POST to /quiz/api/generate/
    ↓
Django view calls quiz_service.generate_quiz()
    ↓
Service client sends request to Quiz Service
    ↓
Quiz Service generates questions
    ↓
Quiz saved locally with questions
    ↓
Frontend redirects to take quiz
    ↓
Questions loaded and displayed
    ↓
User submits answers
    ↓
Results calculated and shown
```

## Configuration

### Service URLs Configuration

Edit `.env` file:
```ini
CHAT_SERVICE_URL=http://localhost:8001
DOCUMENT_SERVICE_URL=http://localhost:8002
STT_SERVICE_URL=http://localhost:8003
TTS_SERVICE_URL=http://localhost:8004
QUIZ_SERVICE_URL=http://localhost:8005
```

Or edit `config/settings.py`:
```python
# Backend Service URLs
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://localhost:8000')
CHAT_SERVICE_URL = os.getenv('CHAT_SERVICE_URL', 'http://localhost:8001')
# ... etc
```

### Adding New Service Integration

To add a new microservice:

1. **Create app structure:**
   ```bash
   python manage.py startapp apps/newservice
   ```

2. **Create service client** (`apps/newservice/services.py`):
   ```python
   import requests
   from django.conf import settings
   
   class NewServiceClient:
       def __init__(self):
           self.base_url = settings.NEW_SERVICE_URL
       
       def some_method(self, params):
           response = requests.post(
               f'{self.base_url}/api/endpoint',
               json=params,
               timeout=10
           )
           return response.json()
   ```

3. **Create views** (`apps/newservice/views.py`)

4. **Create models** (`apps/newservice/models.py`)

5. **Create templates** in `templates/newservice/`

6. **Add URLs** (`apps/newservice/urls.py`)

7. **Register in settings** (`config/settings.py`):
   ```python
   INSTALLED_APPS = [
       # ...
       'apps.newservice',
   ]
   ```

8. **Add service URL** to `.env`:
   ```ini
   NEW_SERVICE_URL=http://localhost:PORT
   ```

## Error Handling

The frontend includes error handling for:

### Service Unavailability
```python
except requests.exceptions.RequestException as e:
    return {'error': str(e), 'status': 'failed'}
```

### Network Timeouts
```python
response = requests.post(
    url,
    json=data,
    timeout=10  # 10 second timeout
)
```

### JSON Validation
```python
try:
    data = json.loads(request.body)
except json.JSONDecodeError:
    return JsonResponse({'error': 'Invalid JSON'}, status=400)
```

## Logging

Enable logging to track API calls:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Calling {service_name} API")
logger.error(f"Service error: {error}")
```

## Testing Services

### Test Chat Service
```bash
curl -X POST http://localhost:8001/message \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1", "message": "Hello"}'
```

### Test Document Upload
```bash
curl -X POST http://localhost:8002/api/documents/upload \
  -F "file=@document.pdf"
```

### Test STT Service
```bash
curl -X POST http://localhost:8003/api/stt/transcribe \
  -F "file=@audio.mp3"
```

### Test TTS Service
```bash
curl -X POST http://localhost:8004/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "default"}'
```

### Test Quiz Service
```bash
curl -X POST http://localhost:8005/api/quizzes/generate \
  -H "Content-Type: application/json" \
  -d '{"document_id": "1", "notes": "...", "num_questions": 5}'
```

## Performance Optimization

### Caching
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def get_voices(request):
    return tts_service.get_voices()
```

### Async Requests
Use Celery for long-running operations:
```python
from celery import shared_task

@shared_task
def generate_quiz_async(document_id, notes):
    return quiz_service.generate_quiz(document_id, notes)
```

## Deployment Considerations

### Production Checklist
- [ ] Update service URLs to production endpoints
- [ ] Enable HTTPS for API calls
- [ ] Configure CORS properly on backend
- [ ] Set up load balancing if needed
- [ ] Enable caching
- [ ] Configure monitoring and logging
- [ ] Set appropriate timeouts
- [ ] Use environment variables for secrets

## Support

For integration issues:
1. Check backend service logs
2. Verify network connectivity
3. Check service URLs in settings
4. Review error messages in frontend logs
5. Check browser console for JavaScript errors
