from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AddMemberForm, JoinTeamByCodeForm, TeamForm
from .models import Team, TeamMembership
from .permissions import is_team_manager, is_team_member
from .selectors import get_team_memberships, get_teams_for_user
from .services import (
    add_or_update_member,
    create_team,
    join_team_by_code,
    remove_member,
    set_member_role,
)

User = get_user_model()


@login_required
def team_list_view(request):
    teams = get_teams_for_user(request.user)
    return render(request, "teams/team_list.html", {"teams": teams})


@login_required
def team_detail_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not is_team_member(request.user, team):
        return HttpResponseForbidden()

    memberships = get_team_memberships(team)

    return render(
        request,
        "teams/team_detail.html",
        {
            "team": team,
            "memberships": memberships,
            "is_team_manager": is_team_manager(request.user, team),
        },
    )

@login_required
def add_member_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not is_team_manager(request.user, team):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = AddMemberForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            role = form.cleaned_data["role"]

            try:
                add_or_update_member(team, user, role)
                return redirect("team_detail", team_id=team.id)
            except (DatabaseError, IntegrityError):
                messages.error(request, "Не удалось добавить участника.")
    else:
        form = AddMemberForm()

    return render(request, "teams/add_member.html", {
        "form": form,
        "team": team
    })

@login_required
def remove_member_view(request, membership_id):
    membership = get_object_or_404(TeamMembership, id=membership_id)

    if not is_team_manager(request.user, membership.team):
        return HttpResponseForbidden()

    try:
        team_id = remove_member(membership)
    except (DatabaseError, IntegrityError):
        messages.error(request, "Не удалось удалить участника.")
        team_id = membership.team_id

    return redirect("team_detail", team_id=team_id)


@require_POST
@login_required
def membership_set_role_view(request, membership_id):
    membership = get_object_or_404(TeamMembership, id=membership_id)

    if not is_team_manager(request.user, membership.team):
        return HttpResponseForbidden()

    role = request.POST.get("role")
    try:
        role_changed = set_member_role(membership, role)
    except (DatabaseError, IntegrityError):
        messages.error(request, "Не удалось изменить роль участника.")
        return redirect("team_detail", team_id=membership.team_id)

    if not role_changed:
        return redirect("team_detail", team_id=membership.team_id)

    return redirect("team_detail", team_id=membership.team_id)

@require_POST
@login_required
def quick_add_member_view(request):
    user_id = request.POST.get("user_id")
    team_id = request.POST.get("team_id")
    role = request.POST.get("role", "EMPLOYEE")

    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)

    if not is_team_manager(request.user, team):
        return HttpResponseForbidden()

    try:
        _membership, created = add_or_update_member(team, user, role)
    except (DatabaseError, IntegrityError):
        messages.error(request, "Не удалось добавить пользователя в команду.")
        return redirect("user_list")

    if created:
        messages.success(request, f"{user.email} добавлен в команду")
    else:
        messages.success(request, f"{user.email}: роль обновлена")

    return redirect("user_list")

@login_required
def team_create_view(request):
    if request.method == "POST":
        form = TeamForm(request.POST)

        if form.is_valid():
            try:
                team = create_team(form, request.user)
                return redirect("team_detail", team_id=team.id)
            except (DatabaseError, IntegrityError):
                messages.error(request, "Не удалось создать команду.")

    else:
        form = TeamForm()

    return render(request, "teams/team_form.html", {
        "form": form
    })

@login_required
def join_team_by_code_view(request):
    if request.method == "POST":
        form = JoinTeamByCodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                team = join_team_by_code(request.user, code)
            except (DatabaseError, IntegrityError):
                messages.error(request, "Не удалось войти в команду.")
                team = None

            if team:
                return redirect("team_detail", team_id=team.id)

    else:
        form = JoinTeamByCodeForm()

    return render(request, "teams/join_team.html", {
        "form": form
    })
