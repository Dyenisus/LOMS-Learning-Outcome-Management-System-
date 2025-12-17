from django import forms
from .models import Course
from accounts.models import CustomUser


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "program",
            "code",
            "name",
            "description",
            "year",
            "semester",
            "ects",
            "credit",
            "lecturer",   # 🔥 burası eklendi
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lecturer alanında sadece Lecturer rolündekiler listelensin
        self.fields["lecturer"].queryset = CustomUser.objects.filter(
            role=CustomUser.Role.LECTURER
        )
        self.fields["lecturer"].required = False
