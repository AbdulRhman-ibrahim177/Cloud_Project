"""
Quiz URL patterns.
"""
from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.QuizListView.as_view(), name='list'),
    path('generate/', views.QuizGenerateView.as_view(), name='generate'),
    path('<str:quiz_id>/', views.QuizDetailView.as_view(), name='detail'),
    path('<str:quiz_id>/results/', views.QuizResultsView.as_view(), name='results'),
    path('api/generate/', views.generate_quiz, name='api_generate'),
    path('api/<str:quiz_id>/', views.get_quiz, name='api_get'),
    path('api/<str:quiz_id>/submit/', views.submit_quiz, name='api_submit'),
]
