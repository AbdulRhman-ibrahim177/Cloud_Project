import json
import time
from io import BytesIO
from pathlib import Path

import boto3
import yaml
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy.orm import Session

from db import SessionLocal, Document

CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

KAFKA_BOOTSTRAP = config["kafka"]["bootstrap_servers"]
GROUP_ID = config["kafka"]["group_id"]
TOPIC_UPLOADED = config["kafka"]["topics"]["document_uploaded"]
TOPIC_PROCESSED = config["kafka"]["topics"]["document_processed"]
TOPIC_NOTES = config["kafka"]["topics"]["notes_generated"]

BASE_DIR = Path(config["storage"]["base_dir"])
NOTES_DIR = BASE_DIR / "notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)

USE_S3 = bool(config["storage"].get("use_s3", False))
S3_CONFIG = config["storage"].get("s3", {})

s3_client = None
if USE_S3:
    s3_client = boto3.client(
        "s3",
        region_name=S3_CONFIG.get("region"),
        endpoint_url=S3_CONFIG.get("endpoint_url") or None,
    )
    S3_BUCKET = S3_CONFIG["bucket"]
else:
    S3_BUCKET = None

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def process_document_bytes(document_id: str, filename: str, data: bytes) -> str:
    """
    هنا المفروض تعمل:
      - PDF / DOCX parsing
      - Text extraction
      - Summarization عبر LLM أو أي lib
    دلوقتي هنعمل ملخص بسيط placeholder.
    """
    text_preview = data.decode(errors="ignore")
    summary = (
        f"Auto-generated notes for document {filename}.\n\n"
        f"Preview:\n{text_preview[:500]}"
    )
    return summary


def run_worker():
    consumer = KafkaConsumer(
        TOPIC_UPLOADED,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    print("[worker] Listening for document.uploaded events...")

    for msg in consumer:
        payload = msg.value
        doc_id = payload.get("document_id")
        filename = payload.get("filename")
        s3_key = payload.get("s3_key")

        if not doc_id or not filename:
            print("[worker] Invalid message payload, skipping:", payload)
            continue

        print(f"[worker] Processing document {doc_id} ({filename})")

        # 1) جِب الـ file content من S3 أو من local لو لسه بتسند على FS
        file_bytes = b""

        if USE_S3 and s3_client is not None and s3_key:
            try:
                obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
                file_bytes = obj["Body"].read()
            except Exception as e:
                print(f"[worker] Error reading from S3: {e}")
                file_bytes = b""
        else:
            # Fallback: لو عندك نسخة local (اختياري)
            docs_dir = BASE_DIR / "files"
            file_path = docs_dir / f"{doc_id}__{filename}"
            if file_path.exists():
                with open(file_path, "rb") as f:
                    file_bytes = f.read()

        # 2) عمل "processing" وهمي
        notes = process_document_bytes(doc_id, filename, file_bytes)

        # 3) تخزين الـ notes محلياً
        notes_path = NOTES_DIR / f"{doc_id}.txt"
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write(notes)

        # 4) تحديث DB
        db: Session = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.notes_path = str(notes_path)
                doc.status = "processed"
                db.commit()
        finally:
            db.close()

        # 5) Produce document.processed
        producer.send(
            TOPIC_PROCESSED,
            {"document_id": doc_id, "filename": filename, "status": "processed"},
        )

        # 6) Produce notes.generated
        producer.send(
            TOPIC_NOTES,
            {
                "document_id": doc_id,
                "notes_path": str(notes_path),
                "status": "generated",
            },
        )

        producer.flush()
        print(f"[worker] Done. Notes stored at {notes_path}")
        time.sleep(0.1)


if __name__ == "__main__":
    run_worker()
