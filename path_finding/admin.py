# path_finding/admin.py

from django.contrib import admin
from .models import TestSession, TestAnswer

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'date_taken', 'is_complete')
    list_filter = ('is_complete', 'date_taken')

@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_session', 'question_id', 'answer_text')
