from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def sync_student_courses(sender, instance: CustomUser, **kwargs):
    """
    When a student user is created or updated, keep their course enrollments
    in sync based on program + grade. Non-students are cleared out.
    """
    user = instance

    # Safety: if relation isn't ready (e.g. migrations), skip.
    if not hasattr(user, "enrolled_courses"):
        return

    # Only students are auto-enrolled.
    if user.role != CustomUser.Role.STUDENT:
        user.enrolled_courses.clear()
        return

    program_id = getattr(user, "student_program_id", None)
    grade = getattr(user, "student_grade", None)

    if not program_id or not grade:
        user.enrolled_courses.clear()
        return

    from courses.models import Course  # local import to avoid circulars

    courses = Course.objects.filter(
        program_id=program_id,
        year=grade,
    )
    user.enrolled_courses.set(courses)
