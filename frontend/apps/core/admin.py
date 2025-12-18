"""
Admin configuration for Cloud Project Frontend.
"""
from django.contrib import admin
from apps.core.models import UserProfile
from apps.chat.models import Conversation, Message
from apps.documents.models import Document
from apps.stt.models import Transcription
from apps.tts.models import Synthesis
from apps.quiz.models import Quiz, QuizAnswer


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'created_at')
    search_fields = ('content', 'conversation__title')
    list_filter = ('sender', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    search_fields = ('title', 'user__username', 'document_id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('document_id', 'created_at', 'updated_at')


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'status', 'created_at')
    search_fields = ('filename', 'user__username', 'transcription_id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('transcription_id', 'created_at', 'updated_at')


@admin.register(Synthesis)
class SynthesisAdmin(admin.ModelAdmin):
    list_display = ('synthesis_id', 'user', 'voice', 'status', 'created_at')
    search_fields = ('user__username', 'synthesis_id')
    list_filter = ('status', 'voice', 'created_at')
    readonly_fields = ('synthesis_id', 'created_at', 'updated_at')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'difficulty', 'num_questions', 'status', 'score')
    search_fields = ('title', 'user__username', 'quiz_id')
    list_filter = ('status', 'difficulty', 'created_at')
    readonly_fields = ('quiz_id', 'created_at', 'updated_at')


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_id', 'is_correct', 'created_at')
    search_fields = ('quiz__title', 'question_id')
    list_filter = ('is_correct', 'created_at')
    readonly_fields = ('created_at',)
