from django.urls import path
from .views import (
	faculty_program_list,
	program_create,
	program_edit,
	program_delete,
	faculty_member_dashboard,
	faculty_edit,
	faculty_delete
)

app_name = "organizations"

urlpatterns = [
    path("", faculty_program_list, name="faculty_program_list"),  # Student Affairs paneli
    path("programs/new/", program_create, name="program_create"),
	path("programs/<int:pk>/edit/", program_edit, name="program_edit"),
	path("programs/<int:pk>/delete/", program_delete, name="program_delete"),
    path("faculty-member/", faculty_member_dashboard, name="faculty_member_dashboard"),
	path("faculty/<int:pk>/edit/", faculty_edit, name="faculty_edit"),
	path("faculty/<int:pk>/delete/", faculty_delete, name="faculty_delete"),

]
