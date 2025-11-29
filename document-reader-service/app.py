import os
import uuid
import json
from pathlib import Path
from typing import List

import yaml
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from kafka import KafkaProducer

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
META_DIR = BASE_DIR / "meta"
NOTES_DIR = BASE_DIR / "notes"

for d in (DOCS_DIR, META_DIR, NOTES_DIR):
    d.mkdir(parents=True, exist_ok=True)

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


class NotesResponse(BaseModel):
    id: str
    notes: str


app = FastAPI(title="Document Reader Service")


# --------------------------
# Helper functions
# --------------------------
def _meta_path(doc_id: str) -> Path:
    return META_DIR / f"{doc_id}.json"


def _notes_path(doc_id: str) -> Path:
    return NOTES_DIR / f"{doc_id}.txt"


def _file_path(doc_id: str, filename: str) -> Path:
    return DOCS_DIR / f"{doc_id}__{filename}"


def _load_metadata(doc_id: str) -> dict:
    path = _meta_path(doc_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------
# API endpoints
# --------------------------

# POST /api/documents/upload
@app.post("/api/documents/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())
    dest_path = _file_path(doc_id, file.filename)

    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    meta = {
        "id": doc_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }
    with open(_meta_path(doc_id), "w", encoding="utf-8") as f:
        json.dump(meta, f)

    # Event: document.uploaded
    send_event(
        TOPIC_UPLOADED,
        {
            "document_id": doc_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
        },
    )

    return meta


# GET /api/documents/{id}
@app.get("/api/documents/{doc_id}", response_model=DocumentMetadata)
async def get_document(doc_id: str):
    meta = _load_metadata(doc_id)
    return meta


# GET /api/documents/{id}/notes
@app.get("/api/documents/{doc_id}/notes", response_model=NotesResponse)
async def get_notes(doc_id: str):
    path = _notes_path(doc_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Notes not found")
    with open(path, "r", encoding="utf-8") as f:
        notes = f.read()
    return NotesResponse(id=doc_id, notes=notes)


# POST /api/documents/{id}/regenerate-notes
@app.post("/api/documents/{doc_id}/regenerate-notes")
async def regenerate_notes(doc_id: str):
    meta = _load_metadata(doc_id)

    # هنا ممكن تبعت Event جديد لو worker بيعتمد عليه
    send_event(
        TOPIC_PROCESSED,
        {
            "document_id": doc_id,
            "action": "regenerate_notes",
        },
    )

    return {"status": "queued", "document_id": doc_id}


# GET /api/documents
@app.get("/api/documents", response_model=List[DocumentSummary])
async def list_documents():
    docs: List[DocumentSummary] = []
    for meta_file in META_DIR.glob("*.json"):
        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        docs.append(DocumentSummary(id=data["id"], filename=data["filename"]))
    return docs


# DELETE /api/documents/{id}
@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    meta = _load_metadata(doc_id)
    file_path = _file_path(doc_id, meta["filename"])
    notes_path = _notes_path(doc_id)

    for p in [file_path, _meta_path(doc_id), notes_path]:
        if p.exists():
            p.unlink()

    return {"deleted": True, "id": doc_id}
