from django import forms

from .models import Assessment


class DatePickerInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("placeholder", "YYYY-MM-DD")
        super().__init__(*args, **kwargs)


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ["type", "weight_in_course", "max_score", "date"]
        widgets = {
            "date": DatePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        date_field = self.fields.get("date")
        if date_field:
            date_field.input_formats = ["%Y-%m-%d"]

        type_field = self.fields.get("type")
        if type_field:
            type_field.choices = Assessment.AssessmentType.choices

    def build_name(self, course, instance=None):
        """
        Use the selected type label as the display name and ensure uniqueness per course.
        """
        type_value = self.cleaned_data.get("type")
        type_label = dict(self.fields["type"].choices).get(type_value, type_value)
        base_name = type_label or "Assessment"
        existing_names = set(
            Assessment.objects.filter(course=course)
            .exclude(pk=getattr(instance, "pk", None))
            .values_list("name", flat=True)
        )

        name = base_name
        suffix = 2
        while name in existing_names:
            name = f"{base_name} #{suffix}"
            suffix += 1
        return name
