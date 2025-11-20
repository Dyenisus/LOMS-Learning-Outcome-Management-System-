from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT_AFFAIRS = "STUDENT_AFFAIRS", "Student Affairs"
        FACULTY_MEMBER = "FACULTY_MEMBER", "Faculty Member"
        LECTURER = "LECTURER", "Lecturer"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    student_grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Student grade / year (1, 2, 3, 4 ...)",
    )
    
    student_faculty = models.ForeignKey(
        "organizations.Faculty",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
        help_text="Student için kayıtlı olduğu Faculty",
    )

    student_program = models.ForeignKey(
        "organizations.Program",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
        help_text="Student için kayıtlı olduğu program",
    )

    faculty_member_faculty = models.ForeignKey(
        "organizations.Faculty",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="faculty_members",
        help_text="Faculty Member için sorumlu olduğu Faculty",
    )

    lecturer_programs = models.ManyToManyField(
        "organizations.Program",
        blank=True,
        related_name="lecturers",
        help_text="Lecturer için sorumlu olduğu Program(lar)",
    )

    lecturer_curricula = models.ManyToManyField(
        "curriculum.Curriculum",
        blank=True,
        related_name="lecturers",
        help_text="Lecturer için sorumlu olduğu Curriculum(lar)",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN and self.is_superuser

    @property
    def is_student_affairs(self):
        return self.role == self.Role.STUDENT_AFFAIRS

    @property
    def is_faculty_member(self):
        return self.role == self.Role.FACULTY_MEMBER

    @property
    def is_lecturer(self):
        return self.role == self.Role.LECTURER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
