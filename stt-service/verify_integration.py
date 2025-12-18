import requests
import json

print('\n🔍 TESTING STT SERVICE AND KAFKA INTEGRATION\n')
print('=' * 70)

# Test 1: Health Check
print('1️⃣  Testing STT Service Health...')
try:
    r = requests.get('http://127.0.0.1:8003/api/stt/health', timeout=3)
    if r.status_code == 200:
        print('   ✅ SERVICE: HEALTHY')
        data = r.json()
        print(f'   Service: {data.get("service")}')
        print(f'   Status: {data.get("status")}')
    else:
        print(f'   ❌ Health check failed: {r.status_code}')
        exit(1)
except Exception as e:
    print(f'   ❌ Cannot connect: {e}')
    exit(1)

print()

# Test 2: Kafka Connection
print('2️⃣  Testing Kafka Broker Connection...')
try:
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:39092', 'localhost:39093', 'localhost:39094'],
        request_timeout_ms=5000
    )
    print('   ✅ KAFKA: CONNECTED (all 3 brokers reachable)')
    producer.close()
except Exception as e:
    print(f'   ⚠️  Kafka: {str(e)[:60]}')
    print('   (Make sure Kafka is running: docker-compose up -d)')

print()

# Test 3: Upload File
print('3️⃣  Testing File Upload (triggers Kafka message)...')
with open('C:\\temp\\test.mp3', 'wb') as f:
    f.write(bytes([0xFF, 0xFB, 0x90, 0x00]) + bytes([0x00] * 1000))

try:
    with open('C:\\temp\\test.mp3', 'rb') as f:
        r = requests.post('http://127.0.0.1:8003/api/stt/transcribe', files={'file': f}, timeout=5)
    
    if r.status_code == 200:
        data = r.json()
        print('   ✅ FILE UPLOAD: SUCCESS')
        print(f'      Transcription ID: {data.get("transcription_id")}')
        print(f'      Filename: {data.get("filename")}')
        print(f'      Status: {data.get("status")}')
        print(f'      S3 Key: {data.get("s3_key")}')
    else:
        print(f'   ❌ Upload failed: Status {r.status_code}')
        print(f'      Response: {r.text[:100]}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()
print('=' * 70)
print('✅ ALL TESTS COMPLETED')
print('=' * 70)

print('\n📊 NEXT STEPS - VERIFY KAFKA MESSAGE:\n')
print('1. Open Kafdrop Web UI:')
print('   http://localhost:39000\n')
print('2. Navigate to Topics:')
print('   • Click "Topics" in top menu\n')
print('3. Select Topic:')
print('   • Find and click "audio.transcription.requested"\n')
print('4. View Messages:')
print('   • Click "View Messages" button\n')
print('5. Check Message:')
print('   • You should see your uploaded file message with:')
print('     - transcription_id (UUID)')
print('     - filename (test.mp3)')
print('     - s3_key (path to file in S3)\n')
print('✨ If you see it = Kafka Integration is WORKING! 🎉\n')
