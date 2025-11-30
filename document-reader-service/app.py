import os
import uuid
import json
from pathlib import Path
from typing import List

import boto3
import yaml
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from kafka import KafkaProducer

from db import SessionLocal, init_db, Document  # <-- NEW

# --------------------------
# Load config
# --------------------------
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

SERVICE_HOST = config["service"]["host"]
SERVICE_PORT = config["service"]["port"]

KAFKA_BOOTSTRAP = config["kafka"]["bootstrap_servers"]
TOPIC_UPLOADED = config["kafka"]["topics"]["document_uploaded"]
TOPIC_PROCESSED = config["kafka"]["topics"]["document_processed"]
TOPIC_NOTES = config["kafka"]["topics"]["notes_generated"]

BASE_DIR = Path(config["storage"]["base_dir"])
DOCS_DIR = BASE_DIR / "files"
NOTES_DIR = BASE_DIR / "notes"

for d in (DOCS_DIR, NOTES_DIR):
    d.mkdir(parents=True, exist_ok=True)

USE_S3 = bool(config["storage"].get("use_s3", False))
S3_CONFIG = config["storage"].get("s3", {})

# --------------------------
# S3 client (اختياري)
# --------------------------
s3_client = None
if USE_S3:
    s3_client = boto3.client(
        "s3",
        region_name=S3_CONFIG.get("region"),
        endpoint_url=S3_CONFIG.get("endpoint_url") or None,
        # الكريدنشيالز ممكن تيجي من ENV أو profile
    )
    S3_BUCKET = S3_CONFIG["bucket"]
else:
    S3_BUCKET = None

# --------------------------
# Kafka Producer
# --------------------------
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def send_event(topic: str, payload: dict) -> None:
    producer.send(topic, payload)
    producer.flush()


# --------------------------
# Pydantic models
# --------------------------
class DocumentSummary(BaseModel):
    id: str
    filename: str


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    status: str


class NotesResponse(BaseModel):
    id: str
    notes: str


app = FastAPI(title="Document Reader Service with S3 + DB")


@app.on_event("startup")
def on_startup():
    init_db()


# --------------------------
# Helper functions
# --------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _notes_path(doc_id: str) -> Path:
    return NOTES_DIR / f"{doc_id}.txt"


# --------------------------
# API endpoints
# --------------------------

# POST /api/documents/upload
@app.post("/api/documents/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)):
    from fastapi import Depends
    from fastapi import Request  # just to keep fastapi happy

    # manually get session (عشان مبنستخدمش Depends هنا)
    db = SessionLocal()

    try:
        doc_id = str(uuid.uuid4())
        contents = await file.read()
        size = len(contents)

        # 1) تخزين الملف: S3 أو local
        s3_key = None
        if USE_S3 and s3_client is not None:
            s3_key = f"documents/{doc_id}/{file.filename}"
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=contents,
                ContentType=file.content_type or "application/octet-stream",
            )
        else:
            dest_path = DOCS_DIR / f"{doc_id}__{file.filename}"
            with open(dest_path, "wb") as f:
                f.write(contents)

        # 2) حفظ metadata في DB
        doc = Document(
            id=doc_id,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            size=size,
            s3_key=s3_key,
            status="uploaded",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # 3) إرسال event لـ Kafka (document.uploaded)
        payload = {
            "document_id": doc_id,
            "filename": file.filename,
            "content_type": file.content_type or "application/octet-stream",
            "size": size,
            "s3_key": s3_key,
        }
        send_event(TOPIC_UPLOADED, payload)

        return DocumentMetadata(
            id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            size=doc.size,
            status=doc.status,
        )
    finally:
        db.close()


# GET /api/documents/{id}
@app.get("/api/documents/{doc_id}", response_model=DocumentMetadata)
async def get_document(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentMetadata(
            id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            size=doc.size,
            status=doc.status,
        )
    finally:
        db.close()


# GET /api/documents/{id}/notes
@app.get("/api/documents/{doc_id}/notes", response_model=NotesResponse)
async def get_notes(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if not doc.notes_path:
            raise HTTPException(status_code=404, detail="Notes not found")

        notes_path = Path(doc.notes_path)
        if not notes_path.exists():
            raise HTTPException(status_code=404, detail="Notes file missing on disk")

        with open(notes_path, "r", encoding="utf-8") as f:
            notes = f.read()

        return NotesResponse(id=doc_id, notes=notes)
    finally:
        db.close()


# POST /api/documents/{id}/regenerate-notes
@app.post("/api/documents/{doc_id}/regenerate-notes")
async def regenerate_notes(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Event جديد عشان الـ worker يعيد توليد الـ notes
        send_event(
            TOPIC_UPLOADED,  # ممكن تسيبه على نفس التوبيك document.uploaded
            {
                "document_id": doc_id,
                "filename": doc.filename,
                "content_type": doc.content_type,
                "size": doc.size,
                "s3_key": doc.s3_key,
                "action": "regenerate_notes",
            },
        )

        # Optional: عدّل status
        doc.status = "queued"
        db.commit()

        return {"status": "queued", "document_id": doc_id}
    finally:
        db.close()


# GET /api/documents
@app.get("/api/documents", response_model=List[DocumentSummary])
async def list_documents():
    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        return [DocumentSummary(id=d.id, filename=d.filename) for d in docs]
    finally:
        db.close()


# DELETE /api/documents/{id}
@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # 1) امسح من S3 لو موجود
        if USE_S3 and s3_client is not None and doc.s3_key:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=doc.s3_key)

        # 2) امسح ملفات local (notes مثلاً)
        if doc.notes_path:
            p = Path(doc.notes_path)
            if p.exists():
                p.unlink()

        # 3) امسح من DB
        db.delete(doc)
        db.commit()

        return {"deleted": True, "id": doc_id}
    finally:
        db.close()
