from django.urls import path
from .views import evaluation_create_view, my_evaluations_view

urlpatterns = [
    path("create/", evaluation_create_view, name="evaluation_create"),
    path("my/", my_evaluations_view, name="my_evaluations"),
]