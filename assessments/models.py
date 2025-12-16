from django.db import models
from django.conf import settings

from curriculum.models import Curriculum
from outcomes.models import LearningOutcome


class Assessment(models.Model):
    class AssessmentType(models.TextChoices):
        QUIZ = "QUIZ", "Quiz"
        MIDTERM = "MIDTERM", "Midterm"
        FINAL = "FINAL", "Final"
        PROJECT = "PROJECT", "Project"
        OTHER = "OTHER", "Other"

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        default=AssessmentType.OTHER,
    )

    weight_in_course = models.PositiveSmallIntegerField(
        help_text="Contribution to course grade in percent (0-100).",
    )
    max_score = models.PositiveIntegerField(
        default=100,
        help_text="Maximum raw score (e.g. 100).",
    )
    date = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.curriculum.code} - {self.name}"

    class Meta:
        ordering = ["curriculum", "type", "name"]
        unique_together = ("curriculum", "name")
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"


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
        help_text="Percentage of this assessment that targets this LO (0-100).",
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
        help_text="Öğrencinin bu assessment'tan aldığı puan (örn. 85.5).",
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
