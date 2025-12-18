"""
STT URL patterns.
"""
from django.urls import path
from . import views

app_name = 'stt'

urlpatterns = [
    path('', views.STTView.as_view(), name='stt'),
    path('api/upload/', views.upload_audio, name='upload'),
    path('api/<str:transcription_id>/', views.get_transcription, name='get'),
    path('api/list/', views.list_transcriptions, name='list'),
]
