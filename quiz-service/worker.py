"""
Enhanced Kafka Worker for Quiz Service
Consumes: quiz.requested, notes.generated
Produces: quiz.generated
"""
import os
import json
import time
from pathlib import Path
import uuid

import yaml
import requests
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy.orm import Session

from models import Quiz, Question, QuestionType, DifficultyLevel
from database import get_db, init_db
from s3_storage import s3_client
from generator_enhanced import EnhancedQuizGenerator

# ---------------------------
# Load config
# ---------------------------
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

KAFKA_BOOTSTRAP = config["kafka"]["bootstrap_servers"]
GROUP_ID = config["kafka"]["group_id"]

TOPIC_NOTES_GENERATED = config["kafka"]["topics"]["notes_generated"]
TOPIC_QUIZ_REQUESTED = config["kafka"]["topics"]["quiz_requested"]
TOPIC_QUIZ_GENERATED = config["kafka"]["topics"]["quiz_generated"]

# Document Reader Service URL
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://document-reader-service:8000")

# ---------------------------
# Initialize
# ---------------------------
try:
    init_db()
    print("[Worker] Database initialized")
except Exception as e:
    print(f"[Worker] Database initialization failed: {e}")

# ---------------------------
# Kafka Producer
# ---------------------------
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# ---------------------------
# Quiz Generator
# ---------------------------
quiz_generator = EnhancedQuizGenerator(CONFIG_PATH)

# ---------------------------
# Helper Functions
# ---------------------------
def fetch_document_notes(document_id: str) -> str:
    """Fetch document notes from Document Reader Service"""
    try:
        url = f"{DOCUMENT_SERVICE_URL}/api/documents/{document_id}/notes"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("notes", "")
        else:
            print(f"[Worker] Failed to fetch notes for {document_id}: {response.status_code}")
            return ""
    except Exception as e:
        print(f"[Worker] Error fetching notes: {e}")
        return ""


def process_notes_generated(payload: dict):
    """Process notes.generated event - optionally auto-generate quiz"""
    document_id = payload.get("document_id")
    
    if not document_id:
        print("[Worker] Invalid payload - missing document_id")
        return
    
    print(f"[Worker] Received notes.generated for document: {document_id}")
    
    # Fetch notes
    notes = fetch_document_notes(document_id)
    
    if not notes:
        print(f"[Worker] No notes available for document {document_id}")
        return
    
    print(f"[Worker] Notes received for {document_id}. Ready for quiz generation.")
    # Note: Auto-generation is disabled by default
    # Uncomment below to enable automatic quiz generation
    
    # quiz_id = str(uuid.uuid4())
    # generate_quiz_from_notes(quiz_id, document_id, notes)


def process_quiz_requested(payload: dict):
    """Process quiz.requested event - generate quiz asynchronously"""
    quiz_id = payload.get("quiz_id")
    document_id = payload.get("document_id")
    notes = payload.get("notes")
    num_questions = payload.get("num_questions", 5)
    difficulty = payload.get("difficulty", "medium")
    question_types = payload.get("question_types")
    
    if not quiz_id or not document_id:
        print("[Worker] Invalid quiz.requested payload")
        return
    
    print(f"[Worker] Processing quiz.requested for quiz: {quiz_id}")
    
    # If notes not provided, fetch them
    if not notes:
        notes = fetch_document_notes(document_id)
    
    if not notes:
        print(f"[Worker] Cannot generate quiz - no notes available")
        return
    
    # Generate quiz
    generate_quiz_from_notes(
        quiz_id,
        document_id,
        notes,
        num_questions,
        difficulty,
        question_types
    )


def generate_quiz_from_notes(
    quiz_id: str,
    document_id: str,
    notes: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    question_types: list = None
):
    """Generate a quiz and save to database"""
    print(f"[Worker] Generating quiz {quiz_id}...")
    
    try:
        # Generate questions
        quiz_data = quiz_generator.generate_quiz(
            notes=notes,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types or ["multiple_choice", "true_false", "short_answer"]
        )
        
        # Upload to S3
        try:
            s3_key = s3_client.upload_quiz_template(quiz_id, quiz_data)
        except Exception as e:
            print(f"[Worker] S3 upload failed: {e}")
            s3_key = None
        
        # Save to database
        with get_db() as db:
            quiz = Quiz(
                id=quiz_id,
                document_id=document_id,
                title=f"Quiz for Document {document_id}",
                description=f"Auto-generated quiz with {quiz_data['total_questions']} questions",
                difficulty=DifficultyLevel(difficulty),
                total_questions=quiz_data['total_questions'],
                s3_template_key=s3_key
            )
            db.add(quiz)
            
            # Save questions
            for idx, q_data in enumerate(quiz_data['questions']):
                question = Question(
                    id=str(uuid.uuid4()),
                    quiz_id=quiz_id,
                    question_number=idx + 1,
                    question_type=QuestionType(q_data['question_type']),
                    question_text=q_data['question_text'],
                    options=q_data.get('options'),
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data.get('explanation', ''),
                    points=1.0
                )
                db.add(question)
        
        # Publish quiz.generated event
        producer.send(
            TOPIC_QUIZ_GENERATED,
            {
                "quiz_id": quiz_id,
                "document_id": document_id,
                "total_questions": quiz_data['total_questions'],
                "status": "completed",
                "timestamp": time.time()
            }
        )
        producer.flush()
        
        print(f"[Worker] Quiz {quiz_id} generated successfully")
        
    except Exception as e:
        print(f"[Worker] Error generating quiz: {e}")


# ---------------------------
# Worker Loop
# ---------------------------
def run_worker():
    """
    Worker that listens to Kafka events
    Consumes: quiz.requested, notes.generated
    Produces: quiz.generated
    """
    consumer = KafkaConsumer(
        TOPIC_NOTES_GENERATED,
        TOPIC_QUIZ_REQUESTED,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    print(f"[Worker] Quiz Service Worker Started")
    print(f"[Worker] Listening to topics:")
    print(f"  - {TOPIC_NOTES_GENERATED}")
    print(f"  - {TOPIC_QUIZ_REQUESTED}")
    print(f"[Worker] Group ID: {GROUP_ID}")

    for msg in consumer:
        try:
            topic = msg.topic
            payload = msg.value
            
            print(f"[Worker] Received message from topic: {topic}")
            
            if topic == TOPIC_NOTES_GENERATED:
                process_notes_generated(payload)
            
            elif topic == TOPIC_QUIZ_REQUESTED:
                process_quiz_requested(payload)
            
        except Exception as e:
            print(f"[Worker] Error processing message: {e}")
            continue


if __name__ == "__main__":
    print("[Worker] Starting Quiz Service Worker...")
    run_worker()
