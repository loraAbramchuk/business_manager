from .models import Team, TeamMembership


def get_teams_for_user(user):
    return Team.objects.filter(teammembership__user=user).distinct()


def get_team_memberships(team):
    return TeamMembership.objects.filter(team=team)
