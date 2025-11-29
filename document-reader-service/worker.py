import json
import time
from pathlib import Path

import yaml
from kafka import KafkaConsumer, KafkaProducer

# ---------------------------
# Load config
# ---------------------------
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

KAFKA_BOOTSTRAP = config["kafka"]["bootstrap_servers"]
GROUP_ID = config["kafka"]["group_id"]

TOPIC_UPLOADED = config["kafka"]["topics"]["document_uploaded"]
TOPIC_PROCESSED = config["kafka"]["topics"]["document_processed"]
TOPIC_NOTES = config["kafka"]["topics"]["notes_generated"]

BASE_DIR = Path(config["storage"]["base_dir"])
DOCS_DIR = BASE_DIR / "files"
NOTES_DIR = BASE_DIR / "notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# Kafka Producer
# ---------------------------
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# ---------------------------
# Document Processing
# ---------------------------
def process_document(document_id: str, filename: str) -> str:
    file_path = DOCS_DIR / f"{document_id}__{filename}"
    if not file_path.exists():
        return "No content (file not found)."

    try:
        with open(file_path, "rb") as f:
            raw = f.read(2048)
    except Exception:
        raw = b""

    text_preview = raw.decode(errors="ignore")
    summary = (
        f"Auto-generated notes for document {filename}.\n\n"
        f"Preview:\n{text_preview[:500]}"
    )
    return summary

# ---------------------------
# Worker Loop
# ---------------------------
def run_worker():
    consumer = KafkaConsumer(
        TOPIC_UPLOADED,
        TOPIC_PROCESSED,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    print("[worker] Listening for uploaded/processed events...")

    for msg in consumer:
        topic = msg.topic
        payload = msg.value

        doc_id = payload.get("document_id")
        filename = payload.get("filename")
        action = payload.get("action")  # مهم جداً للـ regenerate

        # ---------------------------
        # Case 1 → document.uploaded
        # ---------------------------
        if topic == TOPIC_UPLOADED:
            if not doc_id or not filename:
                print("[worker] Invalid upload payload:", payload)
                continue

            print(f"[worker] (UPLOAD) Processing {doc_id} ({filename})")

            notes = process_document(doc_id, filename)

            notes_path = NOTES_DIR / f"{doc_id}.txt"
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(notes)

            producer.send(TOPIC_PROCESSED, {
                "document_id": doc_id,
                "filename": filename,
                "status": "processed",
            })

            producer.send(TOPIC_NOTES, {
                "document_id": doc_id,
                "notes_path": str(notes_path),
                "status": "generated",
            })

            producer.flush()
            print(f"[worker] Notes stored at {notes_path}")
            continue

        # ---------------------------
        # Case 2 → document.processed (regenerate notes)
        # ---------------------------
        if topic == TOPIC_PROCESSED and action == "regenerate_notes":
            if not doc_id:
                print("[worker] Missing document_id in regenerate request")
                continue

            print(f"[worker] (REGENERATE) Regenerating notes for {doc_id}")

            # Load filename from disk
            file_candidates = list(DOCS_DIR.glob(f"{doc_id}__*"))
            if not file_candidates:
                print("[worker] No file found to regenerate.")
                continue

            file_path = file_candidates[0]
            filename = file_path.name.split("__", 1)[1]

            notes = process_document(doc_id, filename)

            notes_path = NOTES_DIR / f"{doc_id}.txt"
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(notes)

            producer.send(TOPIC_NOTES, {
                "document_id": doc_id,
                "notes_path": str(notes_path),
                "status": "regenerated",
            })

            producer.flush()
            print(f"[worker] Regenerated notes stored at {notes_path}")

        time.sleep(0.1)


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    run_worker()
