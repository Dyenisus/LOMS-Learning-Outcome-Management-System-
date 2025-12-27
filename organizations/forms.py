from django import forms
from django.contrib.auth import get_user_model

from .models import Faculty, Program

CustomUser = get_user_model()


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ["code", "name", "responsible"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Student Affairs only sees Faculty Member accounts when assigning responsibility.
        if "responsible" in self.fields:
            self.fields["responsible"].queryset = (
                CustomUser.objects.filter(role=CustomUser.Role.FACULTY_MEMBER)
                .order_by("username")
            )


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ["code", "name", "faculty"]
