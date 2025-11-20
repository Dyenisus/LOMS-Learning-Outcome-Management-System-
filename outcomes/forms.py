from django import forms
from .models import ProgramOutcome, LearningOutcome


class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ["code", "short_title", "description", "order", "active"]


class LearningOutcomeForm(forms.ModelForm):
    class Meta:
        model = LearningOutcome
        fields = [
            "code",
            "short_title",
            "description",
            "order",
            "active",
        ]
