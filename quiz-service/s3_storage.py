"""
S3 Storage client for quiz templates and generated quizzes
"""
import os
import json
import boto3
from botocore.exceptions import ClientError
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

# Load config
CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Get S3 config
BUCKET_NAME = os.getenv("S3_BUCKET", config["s3"]["bucket_name"])
AWS_REGION = os.getenv("AWS_REGION", config["s3"]["region"])
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", config["s3"].get("access_key"))
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", config["s3"].get("secret_key"))
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", config["s3"].get("endpoint_url"))

# Handle ${VAR} syntax
if isinstance(BUCKET_NAME, str) and BUCKET_NAME.startswith("${"):
    BUCKET_NAME = os.getenv(BUCKET_NAME.strip("${}").split(":-")[1], "quiz-service-storage-dev")
if isinstance(AWS_REGION, str) and AWS_REGION.startswith("${"):
    AWS_REGION = os.getenv(AWS_REGION.strip("${}").split(":-")[1], "us-east-1")
if isinstance(S3_ENDPOINT_URL, str) and S3_ENDPOINT_URL.startswith("${"):
    # Handle ${VAR} or ${VAR:-default} syntax
    S3_ENDPOINT_URL = None  # Set to None if not provided, which means use AWS S3


class S3Client:
    """S3 client for quiz storage"""
    
    def __init__(self):
        """Initialize S3 client"""
        session_kwargs = {}
        
        if AWS_ACCESS_KEY and AWS_SECRET_KEY:
            session_kwargs['aws_access_key_id'] = AWS_ACCESS_KEY
            session_kwargs['aws_secret_access_key'] = AWS_SECRET_KEY
        
        if AWS_REGION:
            session_kwargs['region_name'] = AWS_REGION
        
        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            **session_kwargs
        )
        
        self.bucket_name = BUCKET_NAME
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure the S3 bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"[S3] Using bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    print(f"[S3] Created bucket: {self.bucket_name}")
                except Exception as create_error:
                    print(f"[S3] Warning: Could not create bucket: {create_error}")
            else:
                print(f"[S3] Warning: Could not access bucket: {e}")
    
    def upload_quiz_template(self, quiz_id: str, quiz_data: Dict[Any, Any]) -> str:
        """
        Upload quiz template to S3
        
        Args:
            quiz_id: Quiz identifier
            quiz_data: Quiz data dictionary
            
        Returns:
            S3 key of uploaded template
        """
        try:
            key = f"quizzes/{quiz_id}/template.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(quiz_data, indent=2, ensure_ascii=False).encode('utf-8'),
                ContentType='application/json'
            )
            
            print(f"[S3] Uploaded quiz template: {key}")
            return key
            
        except Exception as e:
            print(f"[S3] Error uploading quiz template: {e}")
            raise
    
    def get_quiz_template(self, s3_key: str) -> Optional[Dict[Any, Any]]:
        """
        Retrieve quiz template from S3
        
        Args:
            s3_key: S3 key of the template
            
        Returns:
            Quiz data dictionary or None
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            data = json.loads(response['Body'].read().decode('utf-8'))
            print(f"[S3] Retrieved quiz template: {s3_key}")
            return data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                print(f"[S3] Quiz template not found: {s3_key}")
                return None
            else:
                print(f"[S3] Error retrieving quiz template: {e}")
                raise
        except Exception as e:
            print(f"[S3] Error retrieving quiz template: {e}")
            raise
    
    def delete_quiz_template(self, s3_key: str) -> bool:
        """
        Delete quiz template from S3
        
        Args:
            s3_key: S3 key of the template
            
        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            print(f"[S3] Deleted quiz template: {s3_key}")
            return True
            
        except Exception as e:
            print(f"[S3] Error deleting quiz template: {e}")
            return False
    
    def list_quiz_templates(self, prefix: str = "quizzes/") -> list:
        """
        List all quiz templates in S3
        
        Args:
            prefix: S3 key prefix
            
        Returns:
            List of S3 keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            keys = []
            if 'Contents' in response:
                keys = [obj['Key'] for obj in response['Contents']]
            
            print(f"[S3] Listed {len(keys)} quiz templates")
            return keys
            
        except Exception as e:
            print(f"[S3] Error listing quiz templates: {e}")
            return []


# Global S3 client instance
s3_client = S3Client()
