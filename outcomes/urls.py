from django.urls import path
from .views import (
    program_outcome_manage,
    program_outcome_edit,
    program_outcome_delete,
    learning_outcome_manage,
    learning_outcome_edit,
    learning_outcome_delete,
	learning_outcome_mapping,
)

app_name = "outcomes"

urlpatterns = [
    path("program/<int:program_id>/po/", program_outcome_manage, name="program_outcome_manage"),
    path("po/<int:pk>/edit/", program_outcome_edit, name="program_outcome_edit"),
    path("po/<int:pk>/delete/", program_outcome_delete, name="program_outcome_delete"),

    path("curriculum/<int:curriculum_id>/lo/", learning_outcome_manage, name="learning_outcome_manage"),
    path("lo/<int:pk>/edit/", learning_outcome_edit, name="learning_outcome_edit"),
    path("lo/<int:pk>/delete/", learning_outcome_delete, name="learning_outcome_delete"),
	path("lo/<int:pk>/mapping/", learning_outcome_mapping, name="learning_outcome_mapping"),
]
