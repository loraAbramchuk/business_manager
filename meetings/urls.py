from django.urls import path
from .views import (
    meeting_list_view,
    meeting_create_view,
    meeting_delete_view,
)

urlpatterns = [
    path("", meeting_list_view, name="meeting_list"),
    path("create/", meeting_create_view, name="meeting_create"),
    path("<int:meeting_id>/delete/", meeting_delete_view, name="meeting_delete"),
]