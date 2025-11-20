from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def sync_student_curricula(sender, instance: CustomUser, **kwargs):
    """
    When a student user is created or updated, keep their curriculum enrollments
    in sync based on program + grade. Non-students are cleared out.
    """
    user = instance

    # Safety: if relation isn't ready (e.g. migrations), skip.
    if not hasattr(user, "enrolled_curricula"):
        return

    # Only students are auto-enrolled.
    if user.role != CustomUser.Role.STUDENT:
        user.enrolled_curricula.clear()
        return

    program_id = getattr(user, "student_program_id", None)
    grade = getattr(user, "student_grade", None)

    if not program_id or not grade:
        user.enrolled_curricula.clear()
        return

    from curriculum.models import Curriculum  # local import to avoid circulars

    curricula = Curriculum.objects.filter(
        program_id=program_id,
        year=grade,
    )
    user.enrolled_curricula.set(curricula)
