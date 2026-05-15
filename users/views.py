from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.views import TokenObtainPairView

from teams.models import Team
from teams.models import TeamMembership
from teams.permissions import user_managed_team_ids

from .forms import RegisterForm, ProfileUpdateForm
from .serializers import CustomTokenObtainPairSerializer

User = get_user_model()


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    return render(request, "users/profile.html")


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def profile_delete_view(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("home")

    return render(request, "users/profile_delete.html")


@login_required
def user_list_view(request):
    users = User.objects.all()
    teams = Team.objects.filter(id__in=user_managed_team_ids(request.user))

    selected_team_id = request.GET.get("team_id")

    if selected_team_id:
        team = teams.filter(id=selected_team_id).first()
    else:
        team = teams.first()

    if team:
        memberships = TeamMembership.objects.filter(team=team)
    else:
        memberships = []

    member_ids = []
    for membership in memberships:
        member_ids.append(membership.user_id)

    return render(
        request,
        "users/user_list.html",
        {
            "users": users,
            "teams": teams,
            "team": team,
            "member_ids": member_ids,
        },
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
