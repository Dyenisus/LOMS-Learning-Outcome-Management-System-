from django.db import models
from django.conf import settings
from organizations.models import Program


class Curriculum(models.Model):
    class Year(models.IntegerChoices):
        YEAR_1 = 1, "1st Year"
        YEAR_2 = 2, "2nd Year"
        YEAR_3 = 3, "3rd Year"
        YEAR_4 = 4, "4th Year"

    class Semester(models.TextChoices):
        FALL = "FALL", "Fall"
        SPRING = "SPRING", "Spring"
        YEARLONG = "YEARLONG", "Year-long"

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="curricula",
    )

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)

    year = models.PositiveSmallIntegerField(
        choices=Year.choices,
        null=True,
        blank=True,
        help_text="Dersin tipik alındığı sınıf (1,2,3,4).",
    )

    semester = models.CharField(
        max_length=16,
        choices=Semester.choices,
        default=Semester.FALL,
    )

    ects = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="ECTS / AKTS",
    )

    credit = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Yerel kredi",
    )

    description = models.TextField(
        blank=True,
        help_text="Ders açıklaması",
    )

    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lecturer_curricula_assigned",
        help_text="Dersin genel sorumlu öğretim üyesi (program bazında).",
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="enrolled_curricula",
        help_text="Bu derse kayıtlı öğrenciler (otomatik atanır).",
    )

    class Meta:
        unique_together = ("program", "code")
        ordering = ["program", "year", "semester", "code"]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.program.code})"

    def save(self, *args, **kwargs):
        """
        Dersin program + year'i belli olduğunda:
        - o programda okuyan
        - o grade'de olan
        tüm öğrencileri otomatik olarak bu derse ekler.
        """
        super().save(*args, **kwargs)

        # year ve program tanımlıysa → auto-enroll
        if self.year and self.program_id:
            from accounts.models import CustomUser  # local import, circular'ı önler

            qs = CustomUser.objects.filter(
                role=CustomUser.Role.STUDENT,
                student_grade=self.year,
                student_program=self.program,
            )
            self.students.set(qs)
