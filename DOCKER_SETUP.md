# Docker Compose - Complete Service Mapping

## Port Configuration

| Service | Port | URL | Status |
|---------|------|-----|--------|
| **Frontend (Django)** | 8000 | http://localhost:8000 | ✅ Main UI |
| **Chat Service** | 8001 | http://localhost:8001 | ✅ Chat API |
| **Document Service** | 8002 | http://localhost:8002 | ✅ Document API |
| **STT Service** | 8003 | http://localhost:8003 | ✅ Speech-to-Text API |
| **TTS Service** | 8004 | http://localhost:8004 | ✅ Text-to-Speech API |
| **Quiz Service** | 8005 | http://localhost:8005 | ✅ Quiz API |
| **Zookeeper** | 2181 | http://localhost:2181 | ✅ Message Queue |
| **Kafka** | 9092 | http://localhost:9092 | ✅ Event Stream |
| **Prometheus** | 9090 | http://localhost:9090 | ✅ Monitoring |
| **Grafana** | 3000 | http://localhost:3000 | ✅ Dashboard |

## Running All Services

### Step 1: Start Docker Compose
```bash
cd Cloud_Project
docker-compose -f cloud-compose.yml up -d
```

### Step 2: Verify Services
```bash
docker-compose ps
```

You should see all services running:
- cloud-frontend
- chat-service
- document-reader-service
- stt-service
- tts-service
- quiz-service
- zookeeper
- kafka
- prometheus
- grafana

### Step 3: Access Services

**Main Frontend Dashboard:**
```
http://localhost:8000
```

**Admin Panel:**
```
http://localhost:8000/admin/
```

**Individual Service APIs:**
- Chat: http://localhost:8001
- Documents: http://localhost:8002
- STT: http://localhost:8003
- TTS: http://localhost:8004
- Quiz: http://localhost:8005

**Monitoring:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Stop Services

```bash
docker-compose -f cloud-compose.yml down
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f chat-service
docker-compose logs -f quiz-service
```

## Fix Issues

### Reset Everything
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

### Rebuild Images
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Check Service Status
```bash
docker-compose ps
```

## Network Info

All services are connected via **cloud_network** (bridge network), so they can communicate using service names:
- `frontend` → http://frontend:8000
- `chat-service` → http://chat-service:8001
- `document-reader-service` → http://document-reader-service:8002
- etc.

## Volumes

- **frontend-media**: User uploads for frontend
- **frontend-static**: Static files for frontend
- **document-data**: Document storage
- **quiz-data**: Quiz storage

## Environment Variables

The `.env` file in root directory should contain:
```env
OPENAI_API_KEY=your-key
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-key
```

## Port Conflict Resolution

✅ **All ports are unique - NO CONFLICTS**
- Frontend: 8000 (was conflicting with Kong/Document, now Fixed)
- Chat: 8001 (new, no conflict)
- Document: 8002 (was 8000, now moved)
- STT: 8003 (already correct)
- TTS: 8004 (was mapping to 8003, now Fixed)
- Quiz: 8005 (was 8004, now Fixed)
- Kafka: 9092 (external), 29092 (internal)
- Zookeeper: 2181
- Prometheus: 9090
- Grafana: 3000
