from django import forms
from django.db.models import Sum

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
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)
        if not self.course and getattr(self.instance, "course_id", None):
            self.course = self.instance.course

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

    def clean_weight_in_course(self):
        weight = self.cleaned_data.get("weight_in_course")
        if weight is None or not self.course:
            return weight

        queryset = Assessment.objects.filter(course=self.course)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        existing_total = (
            queryset.aggregate(total=Sum("weight_in_course")).get("total") or 0
        )

        new_total = existing_total + weight
        if new_total > 100:
            raise forms.ValidationError(
                f"{self.course.code} already uses {existing_total}% of the course grade. "
                f"Adding {weight}% would exceed 100%."
            )
        return weight
