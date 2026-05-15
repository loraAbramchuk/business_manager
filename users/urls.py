from django.urls import path
from .views import (
    register_view,
    logout_view,
    profile_view,
    profile_edit_view,
    profile_delete_view, user_list_view,
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
    path("profile/delete/", profile_delete_view, name="profile_delete"),
    path("", user_list_view, name="user_list"),
]