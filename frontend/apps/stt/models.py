"""
STT models.
"""
from django.db import models
from django.contrib.auth.models import User


class Transcription(models.Model):
    """Audio transcription record."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcriptions')
    transcription_id = models.CharField(max_length=255, unique=True)
    filename = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    s3_key = models.CharField(max_length=500, blank=True)
    text = models.TextField(blank=True)
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
    content_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.status}"
