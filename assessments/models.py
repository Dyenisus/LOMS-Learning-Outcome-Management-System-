from django.db import models
from django.conf import settings

from courses.models import Course
from outcomes.models import LearningOutcome


class Assessment(models.Model):
    class AssessmentType(models.TextChoices):
        QUIZ = "QUIZ", "Quiz"
        MIDTERM = "MIDTERM", "Midterm"
        FINAL = "FINAL", "Final"
        PROJECT = "PROJECT", "Project"
        ATTENDANCE = "ATTENDANCE", "Attendance"

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        default=AssessmentType.ATTENDANCE,
    )

    weight_in_course = models.PositiveSmallIntegerField(
        help_text="Contribution to overall course grade (0-100%).",
    )
    max_score = models.PositiveIntegerField(
        default=100,
        help_text="Maximum achievable raw score.",
    )
    date = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.course.code} - {self.get_type_display()}"

    class Meta:
        ordering = ["course", "type", "date"]
        unique_together = ("course", "name")
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"

    @property
    def type_sequence(self) -> int:
        """
        Sequential number among assessments of the same type within the course.
        """
        if not getattr(self, "id", None) or not getattr(self, "course_id", None):
            return 1

        if not hasattr(self, "_type_sequence_cache"):
            self._type_sequence_cache = (
                self.__class__.objects.filter(
                    course_id=self.course_id,
                    type=self.type,
                    id__lte=self.id,
                ).count()
            )
        return self._type_sequence_cache

    @property
    def type_total(self) -> int:
        if not getattr(self, "course_id", None):
            return 1
        if not hasattr(self, "_type_total_cache"):
            self._type_total_cache = (
                self.__class__
                .objects
                .filter(course_id=self.course_id, type=self.type)
                .count()
            ) or 1
        return self._type_total_cache

    @property
    def display_name(self) -> str:
        """
        Human-friendly label like 'Midterm 2'.
        """
        base = self.get_type_display()
        if self.type_total > 1:
            seq = self.type_sequence
            return f"{base} {seq}"
        return base


class AssessmentLearningOutcome(models.Model):
    """
    Bir assessment hangi LO'ları yüzde kaç etkiliyor?
    Örn: Midterm -> LO1 %40, LO2 %60
    """
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="lo_mappings",
    )
    learning_outcome = models.ForeignKey(
        LearningOutcome,
        on_delete=models.CASCADE,
        related_name="assessment_mappings",
    )
    # Bu assessment içindeki ağırlık (0-100)
    weight_in_assessment = models.PositiveSmallIntegerField(
        help_text="Percentage of this assessment attributed to the LO (0-100%).",
    )

    class Meta:
        unique_together = ("assessment", "learning_outcome")
        verbose_name = "Assessment → LO Mapping"
        verbose_name_plural = "Assessment → LO Mappings"

    def __str__(self):
        return f"{self.assessment} → {self.learning_outcome} ({self.weight_in_assessment}%)"


class StudentAssessmentResult(models.Model):
    """
    Bir öğrencinin belirli bir assessment'tan aldığı not.
    """
    assessment = models.ForeignKey(
        "assessments.Assessment",
        on_delete=models.CASCADE,
        related_name="results",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_results",
    )

    raw_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Student's raw score on this assessment.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assessment", "student")
        verbose_name = "Student Assessment Result"
        verbose_name_plural = "Student Assessment Results"

    def __str__(self):
        return f"{self.student} - {self.assessment} ({self.raw_score})"

    @property
    def percentage_of_assessment(self):
        """
        Assessment.max_score doluysa, öğrencinin yüzdesini döner.
        Örn: raw_score=80, max_score=100 → 80
        """
        if self.raw_score is None or not self.assessment or not self.assessment.max_score:
            return None
        return (self.raw_score / self.assessment.max_score) * 100
