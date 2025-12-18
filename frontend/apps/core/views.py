"""
Core views for the frontend dashboard.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(TemplateView):
    """Home/Dashboard view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cloud Project Dashboard'
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard view."""
    template_name = 'core/dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = [
            {
                'name': 'Chat',
                'icon': 'bi-chat-dots',
                'description': 'Interactive chat with AI',
                'url': '/chat/',
            },
            {
                'name': 'Documents',
                'icon': 'bi-file-text',
                'description': 'Upload and process documents',
                'url': '/documents/',
            },
            {
                'name': 'Speech to Text',
                'icon': 'bi-mic',
                'description': 'Convert audio to text',
                'url': '/stt/',
            },
            {
                'name': 'Text to Speech',
                'icon': 'bi-volume-up',
                'description': 'Convert text to audio',
                'url': '/tts/',
            },
            {
                'name': 'Quiz Generator',
                'icon': 'bi-question-circle',
                'description': 'Generate quizzes from documents',
                'url': '/quiz/',
            },
        ]
        return context
