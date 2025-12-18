"""
STT views.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import stt_service
import json


class STTView(LoginRequiredMixin, TemplateView):
    """Speech to Text interface."""
    template_name = 'stt/stt.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Speech to Text'
        context['service_status'] = stt_service.health_check()
        transcriptions = stt_service.list_transcriptions()
        context['transcriptions'] = transcriptions.get('transcriptions', [])
        return context


@csrf_exempt
@require_http_methods(["POST"])
def upload_audio(request):
    """API endpoint to upload audio for transcription."""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file_obj = request.FILES['file']
        
        # Validate audio file
        if not file_obj.content_type.startswith('audio/'):
            return JsonResponse({'error': 'File must be an audio file'}, status=400)
        
        result = stt_service.transcribe_audio(file_obj)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_transcription(request, transcription_id):
    """API endpoint to get transcription result."""
    try:
        result = stt_service.get_transcription(transcription_id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def list_transcriptions(request):
    """API endpoint to list transcriptions."""
    try:
        result = stt_service.list_transcriptions()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
