from .models import TeamMembership


def user_team_ids(user):
    return TeamMembership.objects.filter(user=user).values_list("team_id", flat=True)


def user_managed_team_ids(user):
    return TeamMembership.objects.filter(
        user=user,
        role=TeamMembership.Role.MANAGER,
    ).values_list("team_id", flat=True)


def is_team_member(user, team):
    return TeamMembership.objects.filter(user=user, team=team).exists()


def is_team_manager(user, team):
    return TeamMembership.objects.filter(
        user=user,
        team=team,
        role=TeamMembership.Role.MANAGER,
    ).exists()
