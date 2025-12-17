from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "program", "year", "semester", "ects", "credit", "lecturer")
    list_filter = ("program", "year", "semester")
    search_fields = ("code", "name")
