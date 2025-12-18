"""
Tests for Core app.
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.core.models import UserProfile


class UserProfileTests(TestCase):
    """Test UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_profile(self):
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.user, self.user)


class HomeViewTests(TestCase):
    """Test Home view."""
    
    def setUp(self):
        self.client = Client()
    
    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
