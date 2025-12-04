"""
Database models for Quiz Service
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class QuestionType(str, enum.Enum):
    """Question type enumeration"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class DifficultyLevel(str, enum.Enum):
    """Difficulty level enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Quiz(Base):
    """Quiz definition table"""
    __tablename__ = "quizzes"
    
    id = Column(String(36), primary_key=True)
    document_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    total_questions = Column(Integer, nullable=False)
    s3_template_key = Column(String(512))  # S3 key for quiz template
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    responses = relationship("QuizResponse", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    """Question table"""
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON)  # For multiple choice: ["A: ...", "B: ...", "C: ...", "D: ..."]
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    points = Column(Float, default=1.0)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class QuizResponse(Base):
    """Quiz response/submission table"""
    __tablename__ = "quiz_responses"
    
    id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(String(36), nullable=True)  # Optional user identification
    total_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="responses")
    answers = relationship("Answer", back_populates="response", cascade="all, delete-orphan")


class Answer(Base):
    """Individual answer table"""
    __tablename__ = "answers"
    
    id = Column(String(36), primary_key=True)
    response_id = Column(String(36), ForeignKey("quiz_responses.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Integer, nullable=False)  # 0 or 1
    points_earned = Column(Float, nullable=False)
    
    # Relationships
    response = relationship("QuizResponse", back_populates="answers")
    question = relationship("Question", back_populates="answers")
