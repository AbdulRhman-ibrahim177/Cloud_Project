"""
Chat views.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import chat_service
import json


class ChatView(LoginRequiredMixin, TemplateView):
    """Main chat interface."""
    template_name = 'chat/chat.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chat'
        context['user_id'] = self.request.user.id
        return context


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """API endpoint to send chat message."""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not message or not user_id:
            return JsonResponse(
                {'error': 'Missing user_id or message'},
                status=400
            )
        
        # Call chat service
        result = chat_service.send_message(user_id, message)
        
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
