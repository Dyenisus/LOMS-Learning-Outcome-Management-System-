from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path(
        "curriculum/<int:curriculum_id>/",
        views.assessment_manage,
        name="assessment_manage",
    ),
    path(
        "assessment/<int:pk>/edit/",
        views.assessment_edit,
        name="assessment_edit",
    ),
    path(
        "assessment/<int:pk>/delete/",
        views.assessment_delete,
        name="assessment_delete",
    ),
    path(
        "assessment/<int:pk>/lo-mapping/",
        views.assessment_lo_mapping,
        name="assessment_lo_mapping",
    ),
	path(
		"<int:pk>/grades/",
		views.assessment_grade_manage,
		name="assessment_grade_manage",
	),

]
