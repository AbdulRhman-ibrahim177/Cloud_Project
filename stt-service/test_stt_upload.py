#!/usr/bin/env python3
"""
Test STT API with audio file upload
Creates test audio and sends it to STT service
"""
import requests
import json
from pathlib import Path
import sys

# Configuration
STT_URL = "http://127.0.0.1:8003"
UPLOAD_ENDPOINT = f"{STT_URL}/api/stt/transcribe"
HEALTH_ENDPOINT = f"{STT_URL}/api/stt/health"

def test_health():
    """Test if STT service is running"""
    try:
        print("🔍 Checking STT Service...")
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}\n")
            return True
        else:
            print(f"❌ Service returned: {response.status_code}\n")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to STT Service: {e}")
        print("   Start it with: python run.py\n")
        return False

def create_test_audio(filepath):
    """Create a test audio file"""
    print(f"📁 Creating test audio file: {filepath}")
    # Create a minimal MP3 header + dummy data
    audio_data = bytes([0xFF, 0xFB, 0x90, 0x00]) + bytes([0x00] * 1000)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    Path(filepath).write_bytes(audio_data)
    print(f"✅ File created: {Path(filepath).stat().st_size} bytes\n")
    return filepath

def upload_audio(filepath):
    """Upload audio file to STT service"""
    try:
        print(f"📤 Uploading file: {Path(filepath).name}")
        
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload Successful!\n")
            print("📋 Response:")
            print(json.dumps(data, indent=2))
            print()
            return data
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Response: {response.text}\n")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}\n")
        return None

def check_kafka():
    """Check if messages arrived in Kafka"""
    print("🔍 Checking Kafka Topics...")
    print("\n📌 Expected messages:")
    print("   1. audio.transcription.requested - When file is uploaded")
    print("   2. audio.transcription.completed - When transcription is done\n")
    print("📊 View messages at:")
    print("   • Web UI: http://localhost:39000 (Kafdrop)")
    print("   • Terminal: python monitor_kafka.py\n")

if __name__ == "__main__":
    print("=" * 80)
    print("🎤 STT SERVICE TEST")
    print("=" * 80)
    print()
    
    # 1. Check service health
    if not test_health():
        sys.exit(1)
    
    # 2. Create test audio
    audio_file = "C:\\temp\\test_audio.mp3"
    create_test_audio(audio_file)
    
    # 3. Upload audio
    result = upload_audio(audio_file)
    
    if result:
        # 4. Check Kafka
        check_kafka()
        print("=" * 80)
        print("✨ Test Complete! Check Kafka topics to see messages.")
        print("=" * 80)
    else:
        print("=" * 80)
        print("❌ Test Failed")
        print("=" * 80)
