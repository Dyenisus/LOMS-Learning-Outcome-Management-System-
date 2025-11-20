from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "users/create/",
        views.user_create,
        name="user_create",
    ),
    path(
        "users/<int:pk>/edit/",
        views.user_edit,
        name="user_edit",
    ),
    path(
        "users/<int:pk>/delete/",
        views.user_delete,
        name="user_delete",
    ),
    path(
        "redirect/",
        views.role_redirect,
        name="role_redirect",
    ),
    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),
	path(
        "student/curriculum/<int:curriculum_id>/",
        views.student_course_detail,
        name="student_course_detail",
    ),
]
