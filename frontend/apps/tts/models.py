"""
TTS models.
"""
from django.db import models
from django.contrib.auth.models import User


class Synthesis(models.Model):
    """Text-to-speech synthesis record."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='syntheses')
    synthesis_id = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    voice = models.CharField(max_length=100, default='default')
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    s3_key = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('queued', 'Queued'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='queued'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Synthesis {self.synthesis_id} - {self.status}"
