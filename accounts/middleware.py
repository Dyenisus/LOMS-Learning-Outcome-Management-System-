from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """
    If a user is flagged with must_change_password, redirect every request to the
    password change screen until they update it. Logout and the change page itself
    remain accessible so they can exit or complete the flow.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and getattr(request.user, "must_change_password", False)
        ):
            path = request.path
            allowed_prefixes = (
                reverse("accounts:password_change"),
                reverse("accounts:logout"),
                reverse("accounts:login"),
            )

            is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
            is_static = settings.STATIC_URL and path.startswith(settings.STATIC_URL)

            if not is_allowed and not is_static:
                return redirect("accounts:password_change")

        response = self.get_response(request)
        return response
