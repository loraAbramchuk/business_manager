from django.urls import path

from .views import (
    add_member_view,
    join_team_by_code_view,
    membership_set_role_view,
    quick_add_member_view,
    remove_member_view,
    team_create_view,
    team_detail_view,
    team_list_view,
)

urlpatterns = [
    path("list/", team_list_view, name="team_list"),
    path("create/", team_create_view, name="team_create"),
    path("join/", join_team_by_code_view, name="join_team"),
    path("remove-member/<int:membership_id>/", remove_member_view, name="remove_member"),
    path(
        "membership/<int:membership_id>/role/",
        membership_set_role_view,
        name="membership_set_role",
    ),
    path("quick-add/", quick_add_member_view, name="quick_add_member"),
    path("<int:team_id>/", team_detail_view, name="team_detail"),
    path("<int:team_id>/add-member/", add_member_view, name="add_member"),
]
