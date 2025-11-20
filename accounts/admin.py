from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")

    fieldsets = UserAdmin.fieldsets + (
        ("Role & Extra Info", {
            "fields": (
                "role",
                "phone",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role & Extra Info", {
            "fields": (
                "email",
                "role",
                "phone",
            )
        }),
    )
