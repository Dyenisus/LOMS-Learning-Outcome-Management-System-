from django.test import TestCase

from assessments.forms import AssessmentForm
from assessments.models import Assessment
from organizations.models import Faculty, Program
from courses.models import Course


class AssessmentFormTests(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(code="ENG", name="Engineering")
        self.program = Program.objects.create(code="CSE", name="Computer Science", faculty=self.faculty)
        self.course = Course.objects.create(program=self.program, code="CSE101", name="Intro to CSE")

    def test_weight_must_be_positive(self):
        form = AssessmentForm(
            data={
                "type": Assessment.AssessmentType.MIDTERM,
                "weight_in_course": 0,
                "max_score": 100,
                "date": "2025-01-01",
            },
            course=self.course,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("weight_in_course", form.errors)

    def test_weight_cannot_exceed_remaining_percentage(self):
        Assessment.objects.create(
            course=self.course,
            type=Assessment.AssessmentType.MIDTERM,
            name="Midterm 1",
            weight_in_course=90,
            max_score=100,
        )

        form = AssessmentForm(
            data={
                "type": Assessment.AssessmentType.FINAL,
                "weight_in_course": 20,
                "max_score": 100,
                "date": "2025-01-02",
            },
            course=self.course,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("weight_in_course", form.errors)

    def test_valid_weight_passes(self):
        form = AssessmentForm(
            data={
                "type": Assessment.AssessmentType.QUIZ,
                "weight_in_course": 10,
                "max_score": 50,
                "date": "2025-01-03",
            },
            course=self.course,
        )
        self.assertTrue(form.is_valid(), form.errors)
