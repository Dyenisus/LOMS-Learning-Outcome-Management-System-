from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("org/", include("organizations.urls", namespace="organizations")),
	path("curriculum/", include("curriculum.urls", namespace="curriculum")),
	path("outcomes/", include("outcomes.urls", namespace="outcomes")),
	path("assessments/", include("assessments.urls")),

    path("", RedirectView.as_view(url="/accounts/login/", permanent=False)),
]
