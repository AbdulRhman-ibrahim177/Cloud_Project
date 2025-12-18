import boto3
import uuid
import yaml
import os
from pathlib import Path

# Load configuration
config_path = Path(__file__).parent.parent / "config.yaml"
try:
    with open(config_path) as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Warning: Could not load config.yaml: {e}")
    config = {
        "aws": {
            "bucket": os.getenv("AWS_BUCKET", "stt-service-storage-dev"),
            "region": os.getenv("AWS_REGION", "us-east-1")
        }
    }

s3 = None
BUCKET = config["aws"]["bucket"]

# Try to initialize S3, but don't fail if credentials are missing
try:
    s3 = boto3.client("s3", region_name=config["aws"]["region"])
    print("[OK] S3 client initialized")
except Exception as e:
    print(f"[WARNING] S3 not available (for testing only): {e}")
    s3 = None

def upload_audio(file_bytes: bytes, filename: str):
    """Upload audio file to S3, or skip if S3 is not available"""
    try:
        if s3 is None:
            # S3 not available - generate a mock S3 key for testing
            key = f"uploads/{uuid.uuid4()}_{filename}"
            print(f"[WARNING] S3 not configured - using mock key: {key}")
            return key
        
        key = f"uploads/{uuid.uuid4()}_{filename}"
        s3.put_object(Bucket=BUCKET, Key=key, Body=file_bytes)
        print(f"[OK] Uploaded file to S3: {key}")
        return key
    except Exception as e:
        print(f"[WARNING] Error uploading to S3: {e}")
        # Generate mock key for testing
        key = f"uploads/{uuid.uuid4()}_{filename}"
        print(f"   Using mock S3 key: {key}")
        return key


def get_file_url(key: str):
    """Get S3 file URL"""
    return f"https://{BUCKET}.s3.amazonaws.com/{key}"


def delete_file(key: str):
    """Delete file from S3"""
    try:
        s3.delete_object(Bucket=BUCKET, Key=key)
        print(f"Deleted file from S3: {key}")
    except Exception as e:
        print(f"Error deleting from S3: {e}")
