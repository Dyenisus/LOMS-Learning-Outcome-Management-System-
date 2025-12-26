from django import forms
from .models import ProgramOutcome, LearningOutcome


class ProgramOutcomeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and not getattr(self.user, "is_admin", False):
            # Faculty Member için sade form: code + description
            self.fields.pop("short_title", None)
            self.fields.pop("order", None)

    class Meta:
        model = ProgramOutcome
        fields = ["code", "short_title", "description", "order"]


class LearningOutcomeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and not getattr(self.user, "is_admin", False):
            # Lecturer için sade form: code + description
            self.fields.pop("short_title", None)
            self.fields.pop("order", None)

    class Meta:
        model = LearningOutcome
        fields = [
            "code",
            "short_title",
            "description",
            "order",
        ]
