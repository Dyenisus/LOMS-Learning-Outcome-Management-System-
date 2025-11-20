from django import forms
from .models import Curriculum
from accounts.models import CustomUser


class CurriculumForm(forms.ModelForm):
    class Meta:
        model = Curriculum
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
