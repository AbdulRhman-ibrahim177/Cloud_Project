# STT Service - Testing Guide

## 📋 Overview

This guide explains how to test the STT Service APIs and verify Kafka connectivity.

**Tests include:**
- ✅ Health Check (GET)
- ✅ Create/Upload Audio (POST)
- ✅ Retrieve Single (GET)
- ✅ Retrieve All (GET)
- ✅ Update (PUT)
- ✅ Delete (DELETE)
- ✅ Kafka Message Verification

---

## 🚀 Prerequisites

### 1. Start the Services

Make sure all required services are running:

```bash
# Start Docker containers for Kafka, ZooKeeper, etc.
docker-compose -f cloud-compose.yml up -d

# OR start individual services
cd kafka && docker-compose up -d
cd postgres && docker-compose up -d
cd redis && docker-compose up -d
```

### 2. Start the STT Service

```bash
# Option 1: Run directly
cd stt-service
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8003

# Option 2: Run in Docker
docker-compose up stt-service

# Option 3: Run with custom Kafka brokers
export KAFKA_BROKERS="localhost:39092,localhost:39093,localhost:39094"
python -m uvicorn app:app --host 0.0.0.0 --port 8003
```

---

## 🧪 Testing Options

### Option 1: PowerShell Test Script (Windows)

The easiest way on Windows:

```powershell
# Navigate to stt-service directory
cd stt-service

# Run the PowerShell test script
.\test_api.ps1
```

**Output:**
- Shows all API requests and responses
- Tests CRUD operations
- Indicates success/failure with colors
- Provides instructions for Kafka monitoring

---

### Option 2: Bash Test Script (Linux/Mac)

For Linux/Mac users:

```bash
# Navigate to stt-service directory
cd stt-service

# Make script executable
chmod +x test_api.sh

# Run the script
./test_api.sh
```

---

### Option 3: Python Test Suite

Comprehensive test script with Kafka monitoring:

```bash
cd stt-service

# Install test dependencies
pip install requests kafka-python

# Run the test suite
python test_api_and_kafka.py
```

**Features:**
- Monitors Kafka topics in real-time
- Tests all CRUD operations
- Detailed logging
- Summary report

---

### Option 4: Manual Testing with Curl

Test individual endpoints:

#### 1️⃣ Health Check
```bash
curl -X GET "http://localhost:8003/api/stt/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "STT Service"
}
```

---

#### 2️⃣ Upload Audio File (POST)
```bash
# Create a test audio file first (or use an existing one)
curl -X POST "http://localhost:8003/api/stt/transcribe" \
  -F "file=@test_audio.wav"
```

**Expected Response:**
```json
{
  "status": "queued",
  "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "STT request queued for processing",
  "filename": "test_audio.wav"
}
```

**Save the `transcription_id` for next steps!**

---

#### 3️⃣ Get Single Transcription (GET)
```bash
# Replace ID with the one from POST response
curl -X GET "http://localhost:8003/api/stt/transcription/550e8400-e29b-41d4-a716-446655440000"
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "test_audio.wav",
  "s3_key": "uploads/550e8400-e29b-41d4-a716-446655440000_test_audio.wav",
  "text": "",
  "status": "queued",
  "content_type": "audio/wav",
  "file_size": 44144
}
```

---

#### 4️⃣ List All Transcriptions (GET)
```bash
curl -X GET "http://localhost:8003/api/stt/transcriptions"
```

**Expected Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "test_audio.wav",
    "text": "",
    "status": "queued",
    ...
  }
]
```

---

#### 5️⃣ Update Transcription (PUT)
```bash
curl -X PUT "http://localhost:8003/api/stt/transcription/550e8400-e29b-41d4-a716-446655440000" \
  -d "text=Updated transcription text" \
  -d "status=completed" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Expected Response:**
```json
{
  "status": "updated",
  "transcription": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Updated transcription text",
    "status": "completed",
    ...
  }
}
```

---

#### 6️⃣ Delete Transcription (DELETE)
```bash
curl -X DELETE "http://localhost:8003/api/stt/transcription/550e8400-e29b-41d4-a716-446655440000"
```

**Expected Response:**
```json
{
  "status": "deleted",
  "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Transcription deleted successfully"
}
```

---

## 📊 Kafka Message Verification

### Monitor Kafka Topics

Open a terminal and monitor Kafka messages in real-time:

#### Option 1: Using Kafka Console Consumer

```bash
# Monitor 'audio.transcription.requested' topic
kafka-console-consumer --topic audio.transcription.requested \
  --bootstrap-server localhost:39092 \
  --from-beginning

# In another terminal, monitor 'audio.transcription.completed' topic
kafka-console-consumer --topic audio.transcription.completed \
  --bootstrap-server localhost:39092 \
  --from-beginning
```

#### Option 2: Using Python Kafka Consumer

```bash
# Install kafka-python if not already installed
pip install kafka-python

# Run the consumer script
python -c "
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'audio.transcription.requested',
    'audio.transcription.completed',
    bootstrap_servers=['localhost:39092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print('Listening to Kafka topics...')
for message in consumer:
    print(f'Topic: {message.topic}')
    print(f'Message: {json.dumps(message.value, indent=2)}')
    print('---')
"
```

---

## 📝 Expected Kafka Messages

### When POST Upload Occurs

**Topic:** `audio.transcription.requested`

```json
{
  "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "test_audio.wav",
  "content_type": "audio/wav",
  "s3_key": "uploads/550e8400-e29b-41d4-a716-446655440000_test_audio.wav",
  "file_size": 44144
}
```

### When Worker Processes Audio

**Topic:** `audio.transcription.completed`

```json
{
  "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcription": "Transcribed text here...",
  "filename": "test_audio.wav",
  "s3_key": "uploads/550e8400-e29b-41d4-a716-446655440000_test_audio.wav"
}
```

---

## ✅ Verification Checklist

- [ ] Health check returns 200 status
- [ ] POST upload returns valid transcription_id
- [ ] Message appears on `audio.transcription.requested` topic
- [ ] GET retrieves the uploaded transcription
- [ ] GET all returns list including new transcription
- [ ] PUT successfully updates transcription data
- [ ] DELETE removes transcription (404 on subsequent GET)
- [ ] Kafka consumer receives messages from both topics

---

## 🔍 Troubleshooting

### Service Not Running?
```bash
# Check if service is running
curl http://localhost:8003/api/stt/health

# If not, start it:
cd stt-service
python -m uvicorn app:app --host 0.0.0.0 --port 8003
```

### Kafka Connection Issues?
```bash
# Check Kafka is running
docker-compose ps

# Verify Kafka broker connectivity
python -c "
from kafka import KafkaProducer
try:
    producer = KafkaProducer(bootstrap_servers=['localhost:39092'])
    print('✅ Kafka connection successful!')
except Exception as e:
    print(f'❌ Kafka connection failed: {e}')
"
```

### Audio File Issues?
```bash
# Create a valid test audio file
python3 << 'EOF'
import struct

sample_rate = 44100
duration = 1
num_samples = sample_rate * duration

wav_header = struct.pack(
    '<4sI4s4sIHHIIHH4sI',
    b'RIFF',
    36 + num_samples * 2,
    b'WAVE',
    b'fmt ',
    16, 1, 1,
    sample_rate,
    sample_rate * 2,
    2, 16,
    b'data',
    num_samples * 2
)

audio_data = struct.pack('<' + 'h' * num_samples, *([0] * num_samples))

with open('test_audio.wav', 'wb') as f:
    f.write(wav_header + audio_data)

print("✅ test_audio.wav created")
EOF
```

---

## 📊 Test Results Template

Use this template to document your test results:

```
Date: _________________
Service Version: _______

Test Results:
- Health Check:              [ ] PASS [ ] FAIL
- POST Upload:              [ ] PASS [ ] FAIL
- GET Single:               [ ] PASS [ ] FAIL
- GET All:                  [ ] PASS [ ] FAIL
- PUT Update:               [ ] PASS [ ] FAIL
- DELETE:                   [ ] PASS [ ] FAIL
- Kafka Messages Received:  [ ] YES  [ ] NO

Notes:
_________________________________
_________________________________
```

---

## 🎓 API Specification

### Base URL
```
http://localhost:8003
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stt/health` | Health check |
| POST | `/api/stt/transcribe` | Upload audio |
| GET | `/api/stt/transcription/{tid}` | Get single |
| GET | `/api/stt/transcriptions` | Get all |
| PUT | `/api/stt/transcription/{tid}` | Update |
| DELETE | `/api/stt/transcription/{tid}` | Delete |

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

---

**Happy Testing! 🚀**
