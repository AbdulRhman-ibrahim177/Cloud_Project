"""
Quiz models.
"""
from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """Quiz record."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    quiz_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    document_id = models.CharField(max_length=255)
    difficulty = models.CharField(
        max_length=50,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )
    num_questions = models.IntegerField(default=5)
    questions = models.JSONField(default=dict)  # Store questions as JSON
    status = models.CharField(
        max_length=50,
        choices=[
            ('created', 'Created'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='created'
    )
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class QuizAnswer(models.Model):
    """User's quiz answer."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='answers')
    question_id = models.CharField(max_length=255)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer for question {self.question_id}"
