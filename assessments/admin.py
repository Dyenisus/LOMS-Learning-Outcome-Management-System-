from django.contrib import admin
from .models import Assessment, AssessmentLearningOutcome, StudentAssessmentResult


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("name", "curriculum", "type", "weight_in_course", "max_score")
    list_filter = ("type", "curriculum__program")


@admin.register(AssessmentLearningOutcome)
class AssessmentLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ("assessment", "learning_outcome", "weight_in_assessment")


@admin.register(StudentAssessmentResult)
class StudentAssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("assessment", "student", "raw_score", "created_at")
    list_filter = ("assessment__curriculum",)
    search_fields = ("student__username", "student__first_name", "student__last_name")
