from django import forms
from .models import ProgramOutcome, LearningOutcome


class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ["code", "description"]


class LearningOutcomeForm(forms.ModelForm):
    class Meta:
        model = LearningOutcome
        fields = [
            "code",
            "description",
        ]
