from django.db import models
from organizations.models import Program
from curriculum.models import Curriculum


class ProgramOutcome(models.Model):
    """
    Program-based PO (Program Outcome). Example: PO1 
    "Identifying and solving engineering problems...""
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="program_outcomes",
    )

    code = models.CharField(
        max_length=20,
        help_text="PO code (e.g., PO1, PLO2...)",
    )

    short_title = models.CharField(
        max_length=255,
        help_text="Short title (e.g., Problem solving)",
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description",
    )

    order = models.PositiveSmallIntegerField(
        default=1,
        help_text="For sorting in lists",
    )

    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("program", "code")
        ordering = ["program", "order", "code"]

    def __str__(self):
        return f"{self.program.code} - {self.code}: {self.short_title}"


class LearningOutcome(models.Model):
    """
   Course-based LO (Course Learning Outcome).
   The lecturer will manage this. LO 
   → can be linked to one or more POs.
    """
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="learning_outcomes",
    )

    code = models.CharField(
        max_length=20,
        help_text="LO code (e.g., LO1)",
    )

    short_title = models.CharField(
        max_length=255,
        help_text="Short title (e.g., Explanation of key concepts)",
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description",
    )

    order = models.PositiveSmallIntegerField(
        default=1,
        help_text="In-course LO ranking",
    )

    active = models.BooleanField(default=True)

    program_outcomes = models.ManyToManyField(
        "outcomes.ProgramOutcome",
        through="LearningOutcomeProgramOutcome",
        related_name="learning_outcomes",
        blank=True,
    )

    class Meta:
        unique_together = ("curriculum", "code")
        ordering = ["curriculum", "order", "code"]

    def __str__(self):
        return f"{self.curriculum.code} - {self.code}: {self.short_title}"

class LearningOutcomeProgramOutcome(models.Model):
    learning_outcome = models.ForeignKey(
        LearningOutcome,
        on_delete=models.CASCADE,
        related_name="lo_po_mappings",
    )
    program_outcome = models.ForeignKey(
        ProgramOutcome,
        on_delete=models.CASCADE,
        related_name="po_lo_mappings",
    )
    weight = models.PositiveSmallIntegerField(
        default=0,
        help_text="This LO's contribution to this PO in percent (0–100).",
    )

    class Meta:
        unique_together = ("learning_outcome", "program_outcome")

    def __str__(self):
        return f"{self.learning_outcome} -> {self.program_outcome} ({self.weight}%)"
