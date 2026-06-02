from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from tasks.views import (
    TaskViewSet,
    calendar_day_view,
    calendar_month_view,
    calendar_view,
)
from users.views import CustomTokenObtainPairView


api_router = DefaultRouter()
api_router.register("tasks", TaskViewSet, basename="tasks")

api_urlpatterns = [
    path("", include(api_router.urls)),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

web_urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("users/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("calendar/", calendar_view, name="calendar"),
    path("calendar/month/", calendar_month_view, name="calendar_month"),
    path(
        "calendar/day/<int:year>/<int:month>/<int:day>/",
        calendar_day_view,
        name="calendar_day",
    ),
    path("teams/", include("teams.urls")),
    path("tasks/", include("tasks.urls")),
    path("evaluations/", include("evaluations.urls")),
    path("meetings/", include("meetings.urls")),
]
