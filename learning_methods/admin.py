from django.contrib import admin
from .models import LearningStyleTest

@admin.register(LearningStyleTest)
class LearningStyleTestAdmin(admin.ModelAdmin):
    list_display = ('student', 'date_taken', 'visual_score', 'aural_score', 'read_write_score', 'kinesthetic_score')
    list_filter = ('date_taken', 'student')
    search_fields = ('student__first_name', 'student__last_name')
