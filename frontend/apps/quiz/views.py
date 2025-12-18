"""
Quiz views.
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import quiz_service
import json


class QuizListView(LoginRequiredMixin, TemplateView):
    """List quizzes."""
    template_name = 'quiz/list.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Quizzes'
        quizzes = quiz_service.list_quizzes()
        context['quizzes'] = quizzes.get('quizzes', [])
        return context


class QuizGenerateView(LoginRequiredMixin, TemplateView):
    """Generate new quiz from document."""
    template_name = 'quiz/generate.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate Quiz'
        context['difficulties'] = ['easy', 'medium', 'hard']
        context['question_types'] = ['multiple_choice', 'true_false', 'short_answer']
        return context


class QuizDetailView(LoginRequiredMixin, TemplateView):
    """View and take quiz."""
    template_name = 'quiz/detail.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = kwargs.get('quiz_id')
        context['quiz_id'] = quiz_id
        context['title'] = 'Quiz'
        
        quiz = quiz_service.get_quiz(quiz_id)
        context['quiz'] = quiz
        
        return context


class QuizResultsView(LoginRequiredMixin, TemplateView):
    """View quiz results."""
    template_name = 'quiz/results.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = kwargs.get('quiz_id')
        context['quiz_id'] = quiz_id
        context['title'] = 'Quiz Results'
        
        results = quiz_service.get_quiz_results(quiz_id)
        context['results'] = results
        
        return context


@csrf_exempt
@require_http_methods(["POST"])
def generate_quiz(request):
    """API endpoint to generate quiz."""
    try:
        data = json.loads(request.body)
        document_id = data.get('document_id')
        notes = data.get('notes')
        
        if not document_id or not notes:
            return JsonResponse({'error': 'Missing document_id or notes'}, status=400)
        
        result = quiz_service.generate_quiz(
            document_id=document_id,
            notes=notes,
            title=data.get('title'),
            num_questions=data.get('num_questions', 5),
            difficulty=data.get('difficulty', 'medium'),
            question_types=data.get('question_types')
        )
        
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_quiz(request, quiz_id):
    """API endpoint to submit quiz responses."""
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        result = quiz_service.submit_quiz_response(quiz_id, answers)
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_quiz(request, quiz_id):
    """API endpoint to get quiz."""
    try:
        result = quiz_service.get_quiz(quiz_id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
