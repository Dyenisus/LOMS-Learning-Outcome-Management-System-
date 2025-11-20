from django.contrib import admin
from .models import ProgramOutcome, LearningOutcome


@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ("code", "short_title", "program", "order", "active")
    list_filter = ("program", "active")
    search_fields = ("code", "short_title", "description")


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ("code", "short_title", "curriculum", "order", "active")
    list_filter = ("curriculum", "active")
    search_fields = ("code", "short_title", "description")
    exclude = ("program_outcomes",)
