from django.urls import path
from .views import (
    task_create_view,
    task_delete_view,
    task_detail_view,
    task_list_view,
    task_update_view,
)

urlpatterns = [
    path("", task_list_view, name="task_list"),
    path("create/", task_create_view, name="task_create"),
    path("<int:task_id>/", task_detail_view, name="task_detail"),
    path("<int:task_id>/edit/", task_update_view, name="task_update"),
    path("<int:task_id>/delete/", task_delete_view, name="task_delete"),
]
