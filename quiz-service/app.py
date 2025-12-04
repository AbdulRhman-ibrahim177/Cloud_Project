"""
Quiz Service - Complete Implementation
Meets all technical requirements for Quiz and Exercise Service
"""
import os
import uuid
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import yaml
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from kafka import KafkaProducer
from sqlalchemy.orm import Session

from models import Quiz, Question, QuizResponse, Answer, QuestionType, DifficultyLevel
from database import init_db, get_db_session
from s3_storage import s3_client
from generator import EnhancedQuizGenerator

# --------------------------
# Load config
# --------------------------
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

SERVICE_HOST = config["service"]["host"]
SERVICE_PORT = config["service"]["port"]

KAFKA_BOOTSTRAP = config["kafka"]["bootstrap_servers"]
TOPIC_QUIZ_REQUESTED = config["kafka"]["topics"]["quiz_requested"]
TOPIC_QUIZ_GENERATED = config["kafka"]["topics"]["quiz_generated"]

# --------------------------
# Initialize Database
# --------------------------
try:
    init_db()
    print("[App] Database initialized")
except Exception as e:
    print(f"[App] Warning: Database initialization failed: {e}")

# --------------------------
# Kafka Producer
# --------------------------
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    print("[App] Kafka producer initialized")
except Exception as e:
    print(f"[App] Warning: Kafka producer failed: {e}")
    producer = None


def send_event(topic: str, payload: dict) -> None:
    """Send event to Kafka topic."""
    if producer:
        try:
            producer.send(topic, payload)
            producer.flush()
            print(f"[Kafka] Sent event to {topic}")
        except Exception as e:
            print(f"[Kafka] Error sending event: {e}")


# --------------------------
# Quiz Generator
# --------------------------
quiz_generator = EnhancedQuizGenerator(CONFIG_PATH)


# --------------------------
# Pydantic Models
# --------------------------
class QuizGenerateRequest(BaseModel):
    """Request to generate a quiz"""
    document_id: str = Field(..., description="Document ID to generate quiz from")
    notes: str = Field(..., description="Document notes/content")
    title: Optional[str] = Field(None, description="Quiz title")
    num_questions: int = Field(5, ge=1, le=50, description="Number of questions")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, hard")
    question_types: Optional[List[str]] = Field(
        None,
        description="Question types: multiple_choice, true_false, short_answer"
    )


class QuestionResponse(BaseModel):
    """Response model for a question"""
    id: str
    question_number: int
    question_type: str
    question_text: str
    options: Optional[List[str]]
    points: float


class QuizDetailResponse(BaseModel):
    """Detailed quiz response"""
    id: str
    document_id: str
    title: str
    description: Optional[str]
    difficulty: str
    total_questions: int
    questions: List[QuestionResponse]
    created_at: str


class QuizSummaryResponse(BaseModel):
    """Summary quiz response"""
    id: str
    document_id: str
    title: str
    difficulty: str
    total_questions: int
    created_at: str


class SubmitAnswersRequest(BaseModel):
    """Request to submit quiz answers"""
    answers: dict = Field(..., description="Map of question_index to answer")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class QuestionResultResponse(BaseModel):
    """Result for individual question"""
    question_index: int
    question: str
    question_type: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str
    points_earned: float
    max_points: float


class ResultsResponse(BaseModel):
    """Quiz results response"""
    response_id: str
    quiz_id: str
    total_questions: int
    correct_answers: int
    total_points: float
    earned_points: float
    score_percentage: float
    results: List[QuestionResultResponse]
    submitted_at: str


class QuizHistoryResponse(BaseModel):
    """Quiz history item"""
    response_id: str
    quiz_id: str
    quiz_title: str
    score_percentage: float
    submitted_at: str


# --------------------------
# FastAPI App
# --------------------------
app = FastAPI(
    title="Quiz Service",
    description="Quiz and Exercise Service with multiple question types",
    version="1.0.0"
)


# --------------------------
# API Endpoints
# --------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "quiz-service",
        "version": "1.0.0"
    }


@app.post("/api/quiz/generate", response_model=QuizDetailResponse, status_code=201)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db_session)
):
    """
    Generate a quiz from document notes
    
    Technical Requirements Met:
    - POST /api/quiz/generate endpoint
    - S3 storage for quiz templates
    - PostgreSQL for quiz definitions
    - Kafka event: quiz.generated
    - OpenAI SDK + LangChain for generation
    """
    quiz_id = str(uuid.uuid4())
    
    # Send Kafka event: quiz.requested
    send_event(
        TOPIC_QUIZ_REQUESTED,
        {
            "quiz_id": quiz_id,
            "document_id": request.document_id,
            "num_questions": request.num_questions,
            "difficulty": request.difficulty,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
    
    # Generate quiz using AI (OpenAI + LangChain)
    try:
        quiz_data = quiz_generator.generate_quiz(
            notes=request.notes,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            question_types=request.question_types or ["multiple_choice", "true_false", "short_answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
    
    # Upload to S3
    try:
        s3_key = s3_client.upload_quiz_template(quiz_id, quiz_data)
    except Exception as e:
        print(f"[App] S3 upload failed: {e}")
        s3_key = None
    
    # Save to PostgreSQL
    quiz = Quiz(
        id=quiz_id,
        document_id=request.document_id,
        title=request.title or f"Quiz for Document {request.document_id}",
        description=f"Generated quiz with {quiz_data['total_questions']} questions",
        difficulty=DifficultyLevel(request.difficulty),
        total_questions=quiz_data['total_questions'],
        s3_template_key=s3_key
    )
    db.add(quiz)
    
    # Save questions
    questions_response = []
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
        
        questions_response.append(QuestionResponse(
            id=question.id,
            question_number=question.question_number,
            question_type=question.question_type.value,
            question_text=question.question_text,
            options=question.options,
            points=question.points
        ))
    
    db.commit()
    
    # Send Kafka event: quiz.generated
    send_event(
        TOPIC_QUIZ_GENERATED,
        {
            "quiz_id": quiz_id,
            "document_id": request.document_id,
            "total_questions": quiz_data['total_questions'],
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
    
    return QuizDetailResponse(
        id=quiz.id,
        document_id=quiz.document_id,
        title=quiz.title,
        description=quiz.description,
        difficulty=quiz.difficulty.value,
        total_questions=quiz.total_questions,
        questions=questions_response,
        created_at=quiz.created_at.isoformat()
    )


@app.get("/api/quiz/history", response_model=List[QuizHistoryResponse])
async def get_quiz_history(
    user_id: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """
    Get user's quiz history
    
    Technical Requirements Met:
    - GET /api/quiz/history endpoint
    - Retrieves from PostgreSQL
    """
    query = db.query(QuizResponse, Quiz).join(Quiz, QuizResponse.quiz_id == Quiz.id)
    
    if user_id:
        query = query.filter(QuizResponse.user_id == user_id)
    
    if document_id:
        query = query.filter(Quiz.document_id == document_id)
    
    results = query.order_by(QuizResponse.submitted_at.desc()).all()
    
    history = [
        QuizHistoryResponse(
            response_id=response.id,
            quiz_id=response.quiz_id,
            quiz_title=quiz.title,
            score_percentage=response.percentage,
            submitted_at=response.submitted_at.isoformat()
        )
        for response, quiz in results
    ]
    
    return history


@app.get("/api/quiz/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(quiz_id: str, db: Session = Depends(get_db_session)):
    """
    Get quiz questions (without correct answers)
    
    Technical Requirements Met:
    - GET /api/quiz/{id} endpoint
    - Retrieves from PostgreSQL
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.question_number).all()
    
    questions_response = [
        QuestionResponse(
            id=q.id,
            question_number=q.question_number,
            question_type=q.question_type.value,
            question_text=q.question_text,
            options=q.options,
            points=q.points
        )
        for q in questions
    ]
    
    return QuizDetailResponse(
        id=quiz.id,
        document_id=quiz.document_id,
        title=quiz.title,
        description=quiz.description,
        difficulty=quiz.difficulty.value,
        total_questions=quiz.total_questions,
        questions=questions_response,
        created_at=quiz.created_at.isoformat()
    )


@app.post("/api/quiz/{quiz_id}/submit", response_model=ResultsResponse)
async def submit_quiz(
    quiz_id: str,
    request: SubmitAnswersRequest,
    db: Session = Depends(get_db_session)
):
    """
    Submit quiz answers and get results
    
    Technical Requirements Met:
    - POST /api/quiz/{id}/submit endpoint
    - Calculates scores
    - Stores in PostgreSQL
    - Provides detailed feedback
    """
    # Load quiz and questions
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.question_number).all()
    
    # Prepare quiz data for scoring
    quiz_data = {
        "questions": [
            {
                "question_text": q.question_text,
                "question_type": q.question_type.value,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation
            }
            for q in questions
        ]
    }
    
    # Calculate score
    score_result = quiz_generator.calculate_score(quiz_data, request.answers)
    
    # Create quiz response
    response_id = str(uuid.uuid4())
    quiz_response = QuizResponse(
        id=response_id,
        quiz_id=quiz_id,
        user_id=request.user_id,
        total_score=score_result['earned_points'],
        max_score=score_result['total_points'],
        percentage=score_result['score_percentage']
    )
    db.add(quiz_response)
    
    # Save individual answers
    for result in score_result['results']:
        question = questions[result['question_index']]
        answer = Answer(
            id=str(uuid.uuid4()),
            response_id=response_id,
            question_id=question.id,
            user_answer=result['user_answer'],
            is_correct=1 if result['is_correct'] else 0,
            points_earned=result['points_earned']
        )
        db.add(answer)
    
    db.commit()
    
    # Prepare response
    results_response = [
        QuestionResultResponse(
            question_index=r['question_index'],
            question=r['question'],
            question_type=r['question_type'],
            user_answer=r['user_answer'],
            correct_answer=r['correct_answer'],
            is_correct=r['is_correct'],
            explanation=r['explanation'],
            points_earned=r['points_earned'],
            max_points=r['max_points']
        )
        for r in score_result['results']
    ]
    
    return ResultsResponse(
        response_id=response_id,
        quiz_id=quiz_id,
        total_questions=score_result['total_questions'],
        correct_answers=score_result['correct_answers'],
        total_points=score_result['total_points'],
        earned_points=score_result['earned_points'],
        score_percentage=score_result['score_percentage'],
        results=results_response,
        submitted_at=quiz_response.submitted_at.isoformat()
    )


@app.get("/api/quiz/{quiz_id}/results", response_model=List[ResultsResponse])
async def get_quiz_results(
    quiz_id: str,
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """
    Get quiz results and feedback
    
    Technical Requirements Met:
    - GET /api/quiz/{id}/results endpoint
    - Retrieves from PostgreSQL
    - Provides detailed feedback
    """
    query = db.query(QuizResponse).filter(QuizResponse.quiz_id == quiz_id)
    
    if user_id:
        query = query.filter(QuizResponse.user_id == user_id)
    
    responses = query.order_by(QuizResponse.submitted_at.desc()).all()
    
    if not responses:
        return []
    
    results_list = []
    for response in responses:
        answers = db.query(Answer).filter(Answer.response_id == response.id).all()
        
        results = []
        for answer in answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question:
                results.append(QuestionResultResponse(
                    question_index=question.question_number - 1,
                    question=question.question_text,
                    question_type=question.question_type.value,
                    user_answer=answer.user_answer,
                    correct_answer=question.correct_answer,
                    is_correct=bool(answer.is_correct),
                    explanation=question.explanation,
                    points_earned=answer.points_earned,
                    max_points=question.points
                ))
        
        results_list.append(ResultsResponse(
            response_id=response.id,
            quiz_id=response.quiz_id,
            total_questions=len(results),
            correct_answers=sum(1 for r in results if r.is_correct),
            total_points=response.max_score,
            earned_points=response.total_score,
            score_percentage=response.percentage,
            results=results,
            submitted_at=response.submitted_at.isoformat()
        ))
    
    return results_list


@app.delete("/api/quiz/{quiz_id}")
async def delete_quiz(quiz_id: str, db: Session = Depends(get_db_session)):
    """
    Delete a quiz
    
    Technical Requirements Met:
    - DELETE /api/quiz/{id} endpoint
    - Deletes from PostgreSQL
    - Deletes from S3
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Delete from S3 if exists
    if quiz.s3_template_key:
        try:
            s3_client.delete_quiz_template(quiz.s3_template_key)
        except Exception as e:
            print(f"[App] S3 deletion failed: {e}")
    
    # Delete from database (cascade will handle questions, responses, answers)
    db.delete(quiz)
    db.commit()
    
    return {"deleted": True, "quiz_id": quiz_id}


@app.get("/api/quiz", response_model=List[QuizSummaryResponse])
async def list_quizzes(
    document_id: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """
    List all quizzes with optional filters
    """
    query = db.query(Quiz)
    
    if document_id:
        query = query.filter(Quiz.document_id == document_id)
    
    if difficulty:
        query = query.filter(Quiz.difficulty == DifficultyLevel(difficulty))
    
    quizzes = query.order_by(Quiz.created_at.desc()).all()
    
    return [
        QuizSummaryResponse(
            id=quiz.id,
            document_id=quiz.document_id,
            title=quiz.title,
            difficulty=quiz.difficulty.value,
            total_questions=quiz.total_questions,
            created_at=quiz.created_at.isoformat()
        )
        for quiz in quizzes
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)
