"""
API utilities and serializers for REST API.
"""
from rest_framework import serializers
from apps.core.models import UserProfile
from apps.chat.models import Conversation, Message
from apps.documents.models import Document
from apps.stt.models import Transcription
from apps.tts.models import Synthesis
from apps.quiz.models import Quiz


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = '__all__'


class SynthesisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Synthesis
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'
