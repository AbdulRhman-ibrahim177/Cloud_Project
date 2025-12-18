# Cloud Project Frontend - Django

A comprehensive Django-based frontend for the Cloud Project microservices platform. This frontend provides a unified interface for all services: Chat, Documents, Speech-to-Text (STT), Text-to-Speech (TTS), and Quiz Generation.

## Features

### 🎯 Core Services
- **Chat Interface**: Real-time AI chat communication
- **Document Management**: Upload and process documents with auto-generated notes
- **Speech to Text**: Convert audio files to text transcriptions
- **Text to Speech**: Synthesize text to natural-sounding speech
- **Quiz Generator**: Automatically generate quizzes from document content

### 🎨 User Interface
- Modern, responsive Bootstrap 5 design
- Real-time status updates
- File upload handling
- Service health monitoring
- Beautiful card-based layouts

### 🔌 Backend Integration
- RESTful API clients for all backend services
- Error handling and fallback mechanisms
- Asynchronous service communication
- Database models for data persistence

## Project Structure

```
frontend/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── config/                  # Django configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── apps/                    # Django applications
│   ├── core/                # Core/Home pages
│   ├── chat/                # Chat service
│   ├── documents/           # Document management
│   ├── stt/                 # Speech to Text
│   ├── tts/                 # Text to Speech
│   └── quiz/                # Quiz generator
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── core/                # Core templates
│   ├── chat/                # Chat templates
│   ├── documents/           # Document templates
│   ├── stt/                 # STT templates
│   ├── tts/                 # TTS templates
│   └── quiz/                # Quiz templates
├── static/                  # Static files (CSS, JS, images)
└── media/                   # User uploads
```

## Installation

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone and navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

   The frontend will be available at `http://localhost:8000`

## Configuration

### Environment Variables (.env)

```ini
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Backend Service URLs
API_GATEWAY_URL=http://localhost:8000
CHAT_SERVICE_URL=http://localhost:8001
DOCUMENT_SERVICE_URL=http://localhost:8002
STT_SERVICE_URL=http://localhost:8003
TTS_SERVICE_URL=http://localhost:8004
QUIZ_SERVICE_URL=http://localhost:8005

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

## Service Endpoints

### Chat
- **GET** `/chat/` - Chat interface
- **POST** `/chat/api/send/` - Send message

### Documents
- **GET** `/documents/` - List documents
- **GET** `/documents/upload/` - Upload page
- **GET** `/documents/<doc_id>/` - Document details
- **POST** `/documents/api/upload/` - Upload document
- **GET** `/documents/api/<doc_id>/notes/` - Get document notes

### Speech to Text
- **GET** `/stt/` - STT interface
- **POST** `/stt/api/upload/` - Upload audio
- **GET** `/stt/api/<transcription_id>/` - Get transcription
- **GET** `/stt/api/list/` - List all transcriptions

### Text to Speech
- **GET** `/tts/` - TTS interface
- **POST** `/tts/api/synthesize/` - Synthesize text
- **GET** `/tts/api/<synthesis_id>/` - Get synthesis
- **GET** `/tts/api/voices/` - Get available voices

### Quiz
- **GET** `/quiz/` - List quizzes
- **GET** `/quiz/generate/` - Generate quiz page
- **GET** `/quiz/<quiz_id>/` - Take quiz
- **GET** `/quiz/<quiz_id>/results/` - View results
- **POST** `/quiz/api/generate/` - Generate quiz
- **POST** `/quiz/api/<quiz_id>/submit/` - Submit quiz

## Running with Docker

You can run the frontend in a Docker container. Create a `Dockerfile` in the frontend directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t cloud-frontend .
docker run -p 8000:8000 --env-file .env cloud-frontend
```

## Development

### Running Migrations

```bash
# Create migrations for changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Running Tests

```bash
pytest
```

### Creating Superuser for Admin

```bash
python manage.py createsuperuser
```

Access admin panel at `/admin/`

## Troubleshooting

### Backend Services Not Connecting
- Verify backend services are running on correct ports
- Check `CHAT_SERVICE_URL`, `DOCUMENT_SERVICE_URL`, etc. in `.env`
- Ensure CORS is enabled on backend services

### Database Issues
```bash
# Reset database
python manage.py flush
python manage.py migrate
```

### Port Already in Use
```bash
# Run on different port
python manage.py runserver 8001
```

## Technology Stack

- **Framework**: Django 4.2
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django built-in
- **HTTP Client**: Python requests library

## Security Considerations

1. Change `SECRET_KEY` in production
2. Set `DEBUG = False` in production
3. Use environment variables for sensitive data
4. Enable HTTPS in production
5. Configure proper ALLOWED_HOSTS
6. Use PostgreSQL instead of SQLite in production
7. Set up proper CORS policies

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up proper static file serving
- [ ] Configure logging
- [ ] Set up monitoring

### Using Gunicorn

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using uWSGI

```bash
pip install uwsgi
uwsgi --http :8000 --wsgi-file config/wsgi.py --master --processes 4
```

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## Support

For issues or questions about the Cloud Project Frontend, please:
1. Check the documentation
2. Review backend service documentation
3. Check backend service logs for errors
4. Verify environment configuration

## License

This project is part of the Cloud Project ecosystem.
