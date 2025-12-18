# 🚀 Quick Start Guide - Cloud Project Frontend

## 5-Minute Setup

### Option 1: Windows (PowerShell)

```powershell
# 1. Navigate to frontend
cd frontend

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Start server
python manage.py runserver
```

**Access Frontend**: `http://localhost:8000`

### Option 2: Linux/Mac (Bash)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Start server
python manage.py runserver
```

**Access Frontend**: `http://localhost:8000`

### Option 3: Using Start Script

**Windows:**
```bash
cd frontend
start.bat
```

**Linux/Mac:**
```bash
cd frontend
chmod +x start.sh
./start.sh
```

### Option 4: Docker

```bash
cd frontend

# Build image
docker build -t cloud-frontend .

# Run container
docker run -p 8000:8000 --env-file .env cloud-frontend
```

**Access Frontend**: `http://localhost:8000`

## Services Ports

Ensure all backend services are running on these ports:

| Service | Port | URL |
|---------|------|-----|
| Frontend | 8000 | http://localhost:8000 |
| Chat Service | 8001 | http://localhost:8001 |
| Document Reader | 8002 | http://localhost:8002 |
| STT Service | 8003 | http://localhost:8003 |
| TTS Service | 8004 | http://localhost:8004 |
| Quiz Service | 8005 | http://localhost:8005 |

## Features Available

### 🗣️ Chat
- Interactive chat with AI
- Message history
- Real-time responses

**Access**: `http://localhost:8000/chat/`

### 📄 Documents
- Upload documents
- Auto-generated notes
- Document management

**Access**: `http://localhost:8000/documents/`

### 🎙️ Speech to Text
- Upload audio files
- Get transcriptions
- View history

**Access**: `http://localhost:8000/stt/`

### 🔊 Text to Speech
- Convert text to audio
- Multiple voice options
- Audio management

**Access**: `http://localhost:8000/tts/`

### 📚 Quiz Generator
- Generate quizzes from documents
- Take quizzes
- View results

**Access**: `http://localhost:8000/quiz/`

## Admin Panel

Create admin user:
```bash
python manage.py createsuperuser
```

Access admin panel:
```
http://localhost:8000/admin/
```

## Troubleshooting

### Services not connecting?
1. Check backend services are running
2. Verify ports in `.env`
3. Check CORS settings on backend

### Database errors?
```bash
python manage.py migrate
```

### Port 8000 already in use?
```bash
python manage.py runserver 8001
```

## Next Steps

1. **Configure environment** - Edit `.env` with your settings
2. **Start backend services** - Ensure all microservices are running
3. **Create admin account** - `python manage.py createsuperuser`
4. **Explore features** - Test each service from the web interface
5. **Check documentation** - Read full README.md for details

## Need Help?

- Check `README.md` for full documentation
- Review backend service logs if features aren't working
- Verify network connectivity between services
- Check browser console for frontend errors

Enjoy using Cloud Project! 🎉
