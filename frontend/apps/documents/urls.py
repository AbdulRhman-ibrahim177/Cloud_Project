"""
Document URL patterns.
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='list'),
    path('upload/', views.DocumentUploadView.as_view(), name='upload'),
    path('<str:doc_id>/', views.DocumentDetailView.as_view(), name='detail'),
    path('api/upload/', views.upload_document, name='api_upload'),
    path('api/<str:doc_id>/notes/', views.get_document_notes, name='api_notes'),
]
