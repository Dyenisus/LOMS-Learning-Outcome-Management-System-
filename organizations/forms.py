from django import forms
from .models import Faculty, Program


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ["code", "name", "description", "responsible"]


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ["code", "name", "description", "faculty", "coordinator"]
