from django.db import models
from django.conf import settings  # <-- eklendi


class Faculty(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    description = models.TextField(
        blank=True,
        help_text="Faculty description",
    )

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="responsible_faculties",
        help_text="Faculty Member responsible for this faculty",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Program(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="programs",
    )

    description = models.TextField(
        blank=True,
        help_text="Program description",
    )

    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordinated_programs",
        help_text="Faculty member/coordinator responsible for the program",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"
