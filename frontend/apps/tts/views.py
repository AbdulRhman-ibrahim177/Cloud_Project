"""
TTS views.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import tts_service
import json


class TTSView(LoginRequiredMixin, TemplateView):
    """Text to Speech interface."""
    template_name = 'tts/tts.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Text to Speech'
        voices = tts_service.get_voices()
        context['voices'] = voices.get('voices', [])
        syntheses = tts_service.list_syntheses()
        context['syntheses'] = syntheses.get('syntheses', [])
        return context


@csrf_exempt
@require_http_methods(["POST"])
def synthesize_text(request):
    """API endpoint to synthesize text to speech."""
    try:
        data = json.loads(request.body)
        text = data.get('text')
        voice = data.get('voice', 'default')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        result = tts_service.synthesize_text(text, voice)
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_synthesis(request, synthesis_id):
    """API endpoint to get synthesis result."""
    try:
        result = tts_service.get_synthesis(synthesis_id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_voices(request):
    """API endpoint to get available voices."""
    try:
        result = tts_service.get_voices()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
