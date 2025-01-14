from django.contrib import admin
from .models import Program, TestSession, TestAnswer, PathFindingLog

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'date_taken', 'is_complete')
    list_filter = ('is_complete', 'date_taken')

@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_session', 'question_id', 'answer_text')

@admin.register(PathFindingLog)
class PathFindingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'student', 'message')
    list_filter = ('timestamp', 'student')
