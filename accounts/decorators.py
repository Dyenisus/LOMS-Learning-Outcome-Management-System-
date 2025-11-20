from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import CustomUser


def role_required(*allowed_roles):
    """
    Örnek:
        @role_required(CustomUser.Role.STUDENT_AFFAIRS)
        @role_required(CustomUser.Role.LECTURER, CustomUser.Role.FACULTY_MEMBER)
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user: CustomUser = request.user

            if user.is_admin or user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied("You do not have permission to access this resource.")
        return _wrapped_view
    return decorator
