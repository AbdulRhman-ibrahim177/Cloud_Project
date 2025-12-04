"""
Enhanced Quiz Generator with LangChain and multiple question types
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
from pydantic import BaseModel, Field

# Try to import LangChain, fall back if not available
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import PydanticOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("[Generator] LangChain not available, using fallback")

import openai


class QuestionSchema(BaseModel):
    """Schema for a single question"""
    question_text: str = Field(description="The question text")
    question_type: str = Field(description="Type: multiple_choice, true_false, or short_answer")
    options: Optional[List[str]] = Field(description="Options for multiple choice (A, B, C, D)")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation of the correct answer")


class QuizSchema(BaseModel):
    """Schema for the complete quiz"""
    questions: List[QuestionSchema] = Field(description="List of questions")


class EnhancedQuizGenerator:
    """Enhanced quiz generator with LangChain and multiple question types"""
    
    def __init__(self, config_path: Path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY") or config.get("openai", {}).get("api_key")
        if api_key and api_key.startswith("${"):
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.api_key = api_key
        self.model = config.get("openai", {}).get("model", "gpt-3.5-turbo")
        self.temperature = config.get("openai", {}).get("temperature", 0.7)
        
        if self.api_key:
            openai.api_key = self.api_key
            
            if LANGCHAIN_AVAILABLE:
                self.llm = ChatOpenAI(
                    model=self.model,
                    temperature=self.temperature,
                    openai_api_key=self.api_key
                )
                print("[Generator] Using LangChain for quiz generation")
            else:
                print("[Generator] Using OpenAI directly for quiz generation")
        else:
            print("[Generator] No API key, will use dummy generation")
    
    def generate_quiz(
        self,
        notes: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate quiz questions from notes
        
        Args:
            notes: Document notes/content
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            question_types: List of question types to include
            
        Returns:
            Dictionary with quiz questions
        """
        if not self.api_key:
            return self._generate_dummy_quiz(notes, num_questions, question_types)
        
        if LANGCHAIN_AVAILABLE and hasattr(self, 'llm'):
            return self._generate_with_langchain(notes, num_questions, difficulty, question_types)
        else:
            return self._generate_with_openai(notes, num_questions, difficulty, question_types)
    
    def _generate_with_langchain(
        self,
        notes: str,
        num_questions: int,
        difficulty: str,
        question_types: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Generate quiz using LangChain"""
        try:
            # Default question types
            if not question_types:
                question_types = ["multiple_choice", "true_false", "short_answer"]
            
            # Calculate distribution
            dist = self._calculate_question_distribution(num_questions, question_types)
            
            # Create output parser
            parser = PydanticOutputParser(pydantic_object=QuizSchema)
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert educational quiz creator."),
                ("user", """Based on the following notes, generate {num_questions} quiz questions with difficulty level: {difficulty}.

Question type distribution:
{distribution}

Notes:
{notes}

{format_instructions}

Important:
- For multiple_choice: provide exactly 4 options labeled A, B, C, D
- For true_false: options should be ["True", "False"]
- For short_answer: options should be null, correct_answer should be a concise answer
- Each question should test understanding of the material
- Provide clear explanations for all answers""")
            ])
            
            # Format distribution
            dist_text = "\n".join([f"- {count} {qtype} questions" for qtype, count in dist.items()])
            
            # Generate
            chain = prompt | self.llm | parser
            result = chain.invoke({
                "num_questions": num_questions,
                "difficulty": difficulty,
                "notes": notes[:3000],
                "distribution": dist_text,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Convert to dict format
            questions = []
            for q in result.questions:
                questions.append({
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation
                })
            
            return {
                "questions": questions,
                "total_questions": len(questions)
            }
            
        except Exception as e:
            print(f"[Generator] LangChain generation failed: {e}")
            return self._generate_with_openai(notes, num_questions, difficulty, question_types)
    
    def _generate_with_openai(
        self,
        notes: str,
        num_questions: int,
        difficulty: str,
        question_types: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Generate quiz using OpenAI directly"""
        try:
            if not question_types:
                question_types = ["multiple_choice", "true_false", "short_answer"]
            
            dist = self._calculate_question_distribution(num_questions, question_types)
            dist_text = "\n".join([f"- {count} {qtype} questions" for qtype, count in dist.items()])
            
            prompt = f"""Based on the following notes, generate {num_questions} quiz questions with difficulty level: {difficulty}.

Question type distribution:
{dist_text}

Notes:
{notes[:3000]}

Format your response as a JSON array with this structure:
[
  {{
    "question_text": "Question here?",
    "question_type": "multiple_choice",
    "options": ["A: Option 1", "B: Option 2", "C: Option 3", "D: Option 4"],
    "correct_answer": "A",
    "explanation": "Explanation here"
  }},
  {{
    "question_text": "True or false statement",
    "question_type": "true_false",
    "options": ["True", "False"],
    "correct_answer": "True",
    "explanation": "Explanation here"
  }},
  {{
    "question_text": "Short answer question?",
    "question_type": "short_answer",
    "options": null,
    "correct_answer": "Expected answer",
    "explanation": "Explanation here"
  }}
]

IMPORTANT: Respond ONLY with the JSON array, no additional text."""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert quiz creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            quiz_data = self._parse_quiz_response(content)
            return quiz_data
            
        except Exception as e:
            print(f"[Generator] OpenAI generation failed: {e}")
            return self._generate_dummy_quiz(notes, num_questions, question_types)
    
    def _calculate_question_distribution(
        self,
        total: int,
        question_types: List[str]
    ) -> Dict[str, int]:
        """Calculate how many of each question type to generate"""
        dist = {}
        per_type = total // len(question_types)
        remainder = total % len(question_types)
        
        for i, qtype in enumerate(question_types):
            dist[qtype] = per_type + (1 if i < remainder else 0)
        
        return dist
    
    def _parse_quiz_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into quiz structure"""
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            questions = json.loads(content)
            
            return {
                "questions": questions,
                "total_questions": len(questions)
            }
        except Exception as e:
            print(f"[Generator] Error parsing response: {e}")
            raise
    
    def _generate_dummy_quiz(
        self,
        notes: str,
        num_questions: int,
        question_types: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Generate dummy quiz for testing"""
        if not question_types:
            question_types = ["multiple_choice", "true_false", "short_answer"]
        
        preview = notes[:200] if notes else "No content available"
        questions = []
        
        dist = self._calculate_question_distribution(num_questions, question_types)
        q_num = 1
        
        for qtype, count in dist.items():
            for i in range(count):
                if qtype == "multiple_choice":
                    questions.append({
                        "question_text": f"Question {q_num}: What concept is discussed in the document?",
                        "question_type": "multiple_choice",
                        "options": [
                            "A: First concept from the content",
                            "B: Second concept from the content",
                            "C: Third concept from the content",
                            "D: Fourth concept from the content"
                        ],
                        "correct_answer": "A",
                        "explanation": f"Based on the content preview: {preview[:100]}..."
                    })
                elif qtype == "true_false":
                    questions.append({
                        "question_text": f"Question {q_num}: The document discusses important concepts.",
                        "question_type": "true_false",
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "explanation": "This is true based on the document content."
                    })
                else:  # short_answer
                    questions.append({
                        "question_text": f"Question {q_num}: Summarize the main idea of the document.",
                        "question_type": "short_answer",
                        "options": None,
                        "correct_answer": "The document discusses key concepts and ideas.",
                        "explanation": "Expected answer should capture the main themes."
                    })
                q_num += 1
        
        return {
            "questions": questions,
            "total_questions": len(questions)
        }
    
    def calculate_score(self, quiz_data: Dict[str, Any], user_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate score for submitted answers
        
        Args:
            quiz_data: Original quiz data with correct answers
            user_answers: User's submitted answers
            
        Returns:
            Dictionary with score details
        """
        questions = quiz_data.get("questions", [])
        total = len(questions)
        correct = 0
        total_points = 0
        earned_points = 0
        results = []
        
        for idx, question in enumerate(questions):
            user_answer = user_answers.get(str(idx), "")
            correct_answer = question["correct_answer"]
            question_type = question.get("question_type", "multiple_choice")
            
            # Calculate if correct based on question type
            if question_type == "short_answer":
                # For short answer, do fuzzy matching
                is_correct = self._check_short_answer(user_answer, correct_answer)
            else:
                # Exact match for multiple choice and true/false
                is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
            
            points = 1.0  # Default 1 point per question
            total_points += points
            
            if is_correct:
                correct += 1
                earned_points += points
            
            results.append({
                "question_index": idx,
                "question": question["question_text"],
                "question_type": question_type,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
                "points_earned": points if is_correct else 0,
                "max_points": points
            })
        
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        
        return {
            "total_questions": total,
            "correct_answers": correct,
            "total_points": total_points,
            "earned_points": earned_points,
            "score_percentage": round(percentage, 2),
            "results": results
        }
    
    def _check_short_answer(self, user_answer: str, correct_answer: str) -> bool:
        """Check if short answer is correct (fuzzy matching)"""
        # Simple fuzzy matching - can be improved with NLP
        user_lower = user_answer.lower().strip()
        correct_lower = correct_answer.lower().strip()
        
        # Exact match
        if user_lower == correct_lower:
            return True
        
        # Contains key terms (at least 60% of correct answer words)
        correct_words = set(correct_lower.split())
        user_words = set(user_lower.split())
        
        if len(correct_words) == 0:
            return False
        
        overlap = len(correct_words.intersection(user_words))
        similarity = overlap / len(correct_words)
        
        return similarity >= 0.6
