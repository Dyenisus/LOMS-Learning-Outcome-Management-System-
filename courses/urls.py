from django.urls import path
from .views import (
    course_list,
    course_create,
    course_edit,
    course_delete,
    lecturer_dashboard,
)

app_name = "courses"

urlpatterns = [
    path("", course_list, name="course_list"),
    path("new/", course_create, name="course_create"),
    path("<int:pk>/edit/", course_edit, name="course_edit"),
    path("<int:pk>/delete/", course_delete, name="course_delete"),
    path("lecturer/", lecturer_dashboard, name="lecturer_dashboard"),
]
