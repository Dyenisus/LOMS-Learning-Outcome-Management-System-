from django.contrib import admin
from .models import Faculty, Program


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "responsible")
    search_fields = ("code", "name")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "faculty", "coordinator")
    list_filter = ("faculty",)
    search_fields = ("code", "name")
