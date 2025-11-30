import boto3
import uuid
import yaml

config = yaml.safe_load(open("config.yaml"))

s3 = boto3.client("s3", region_name=config["aws"]["region"])
BUCKET = config["aws"]["bucket"]

def upload_file(content: bytes, ext="mp3"):
    file_id = str(uuid.uuid4())
    key = f"audio/{file_id}.{ext}"
    s3.put_object(Bucket=BUCKET, Key=key, Body=content)
    return file_id, key

def get_file_url(key: str):
    return f"https://{BUCKET}.s3.amazonaws.com/{key}"

def delete_file(key: str):
    s3.delete_object(Bucket=BUCKET, Key=key)
