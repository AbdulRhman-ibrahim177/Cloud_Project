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

s3 = boto3.client("s3", region_name=config["aws"]["region"])
BUCKET = config["aws"]["bucket"]

def upload_audio(file_bytes: bytes, filename: str):
    """Upload audio file to S3"""
    try:
        key = f"uploads/{uuid.uuid4()}_{filename}"
        s3.put_object(Bucket=BUCKET, Key=key, Body=file_bytes)
        print(f"Uploaded file to S3: {key}")
        return key
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise


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
