"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from tasks.views import calendar_view, calendar_month_view, calendar_day_view
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from users.views import CustomTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("users/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("calendar/", calendar_view, name="calendar"),
    path("teams/", include("teams.urls")),
    path("tasks/", include("tasks.urls")),
    path("evaluations/", include("evaluations.urls")),
    path("meetings/", include("meetings.urls")),
    path("calendar/month/", calendar_month_view, name="calendar_month"),
    path(
        "calendar/day/<int:year>/<int:month>/<int:day>/",
        calendar_day_view,
        name="calendar_day"
    ),

    path("api/", include("config.api_urls")),

    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),

]
