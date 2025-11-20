from django.urls import path
from .views import (
	curriculum_list,
	curriculum_create,
	curriculum_edit,
	curriculum_delete,
	lecturer_dashboard
)

app_name = "curriculum"

urlpatterns = [
    path("", curriculum_list, name="curriculum_list"),
    path("new/", curriculum_create, name="curriculum_create"),
    path("<int:pk>/edit/", curriculum_edit, name="curriculum_edit"),
	path("<int:pk>/delete/", curriculum_delete, name="curriculum_delete"),
	path("lecturer/", lecturer_dashboard, name="lecturer_dashboard"),
]
