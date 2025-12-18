"""
URL configuration for Cloud Project Frontend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    
    # App URLs
    path('', include('apps.core.urls')),
    path('chat/', include('apps.chat.urls')),
    path('documents/', include('apps.documents.urls')),
    path('stt/', include('apps.stt.urls')),
    path('tts/', include('apps.tts.urls')),
    path('quiz/', include('apps.quiz.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
