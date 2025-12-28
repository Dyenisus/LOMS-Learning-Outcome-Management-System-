from django import forms

from .models import ProgramOutcome, LearningOutcome


class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ["code", "description"]

    def __init__(self, *args, **kwargs):
        self.program = kwargs.pop("program", None)
        super().__init__(*args, **kwargs)
        if not self.program and getattr(self.instance, "program_id", None):
            self.program = self.instance.program

    def clean_code(self):
        code = self.cleaned_data.get("code")
        program = self.program or getattr(self.instance, "program", None)
        if code and program:
            qs = ProgramOutcome.objects.filter(program=program, code__iexact=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "A program outcome with this code already exists for this program."
                )
        return code


class LearningOutcomeForm(forms.ModelForm):
    class Meta:
        model = LearningOutcome
        fields = [
            "code",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)
        if not self.course and getattr(self.instance, "course_id", None):
            self.course = self.instance.course

    def clean_code(self):
        code = self.cleaned_data.get("code")
        course = self.course or getattr(self.instance, "course", None)
        if code and course:
            qs = LearningOutcome.objects.filter(course=course, code__iexact=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "A learning outcome with this code already exists for this course."
                )
        return code
