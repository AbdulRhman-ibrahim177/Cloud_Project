"""
Document models.
"""
from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    """Uploaded document."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    document_id = models.CharField(max_length=255, unique=True)
    content_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    status = models.CharField(
        max_length=50,
        choices=[('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='processing'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
