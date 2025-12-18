"""
Document views.
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import document_service
import json


class DocumentListView(LoginRequiredMixin, TemplateView):
    """List documents."""
    template_name = 'documents/list.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Documents'
        documents = document_service.get_documents(self.request.user.id)
        context['documents'] = documents.get('documents', [])
        return context


class DocumentUploadView(LoginRequiredMixin, TemplateView):
    """Upload document."""
    template_name = 'documents/upload.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upload Document'
        return context


class DocumentDetailView(LoginRequiredMixin, TemplateView):
    """View document details and notes."""
    template_name = 'documents/detail.html'
    login_url = 'admin:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc_id = kwargs.get('doc_id')
        context['doc_id'] = doc_id
        context['title'] = 'Document Details'
        
        notes = document_service.get_document_notes(doc_id)
        context['notes'] = notes.get('notes', '')
        
        return context


@csrf_exempt
@require_http_methods(["POST"])
def upload_document(request):
    """API endpoint to upload document."""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file_obj = request.FILES['file']
        result = document_service.upload_document(file_obj)
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_document_notes(request, doc_id):
    """API endpoint to get document notes."""
    try:
        notes = document_service.get_document_notes(doc_id)
        return JsonResponse(notes)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
