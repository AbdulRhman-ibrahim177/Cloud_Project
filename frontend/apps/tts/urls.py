"""
TTS URL patterns.
"""
from django.urls import path
from . import views

app_name = 'tts'

urlpatterns = [
    path('', views.TTSView.as_view(), name='tts'),
    path('api/synthesize/', views.synthesize_text, name='synthesize'),
    path('api/<str:synthesis_id>/', views.get_synthesis, name='get'),
    path('api/voices/', views.get_voices, name='voices'),
]
