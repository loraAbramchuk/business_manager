from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AddMemberForm, JoinTeamByCodeForm, TeamForm
from .models import Team, TeamMembership
from .permissions import is_team_manager, is_team_member

User = get_user_model()


@login_required
def team_list_view(request):
    teams = Team.objects.filter(teammembership__user=request.user).distinct()
    return render(request, "teams/team_list.html", {"teams": teams})


@login_required
def team_detail_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not is_team_member(request.user, team):
        return HttpResponseForbidden()

    memberships = TeamMembership.objects.filter(team=team)

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

            membership, created = TeamMembership.objects.get_or_create(
                team=team,
                user=user,
                defaults={"role": role},
            )
            if not created:
                membership.role = role
                membership.save(update_fields=["role"])

            return redirect("team_detail", team_id=team.id)
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

    team_id = membership.team.id
    membership.delete()

    return redirect("team_detail", team_id=team_id)


@require_POST
@login_required
def membership_set_role_view(request, membership_id):
    membership = get_object_or_404(TeamMembership, id=membership_id)

    if not is_team_manager(request.user, membership.team):
        return HttpResponseForbidden()

    role = request.POST.get("role")
    if role not in (
        TeamMembership.Role.MANAGER,
        TeamMembership.Role.EMPLOYEE,
    ):
        return redirect("team_detail", team_id=membership.team_id)

    membership.role = role
    membership.save(update_fields=["role"])

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

    membership, created = TeamMembership.objects.get_or_create(
        user=user,
        team=team,
        defaults={"role": role}
    )

    if created:
        messages.success(request, f"{user.email} добавлен в команду")
    else:
        membership.role = role
        membership.save(update_fields=["role"])
        messages.success(request, f"{user.email}: роль обновлена")

    return redirect("user_list")

@login_required
def team_create_view(request):
    if request.method == "POST":
        form = TeamForm(request.POST)

        if form.is_valid():
            team = form.save(commit=False)

            team.owner = request.user
            team.save()

            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role=TeamMembership.Role.MANAGER,
            )

            return redirect("team_detail", team_id=team.id)

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

            team = Team.objects.filter(join_code=code).first()

            if team:
                TeamMembership.objects.get_or_create(
                    team=team,
                    user=request.user,
                    defaults={"role": TeamMembership.Role.EMPLOYEE},
                )

                return redirect("team_detail", team_id=team.id)

    else:
        form = JoinTeamByCodeForm()

    return render(request, "teams/join_team.html", {
        "form": form
    })
