"""
Chat URL patterns.
"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatView.as_view(), name='chat'),
    path('api/send/', views.send_message, name='send_message'),
]
