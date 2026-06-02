from .models import Team, TeamMembership


def add_or_update_member(team, user, role):
    membership, created = TeamMembership.objects.get_or_create(
        team=team,
        user=user,
        defaults={"role": role},
    )

    if not created:
        membership.role = role
        membership.save(update_fields=["role"])

    return membership, created


def remove_member(membership):
    team_id = membership.team_id
    membership.delete()
    return team_id


def set_member_role(membership, role):
    if role not in (
        TeamMembership.Role.MANAGER,
        TeamMembership.Role.EMPLOYEE,
    ):
        return False

    membership.role = role
    membership.save(update_fields=["role"])
    return True


def create_team(form, owner):
    team = form.save(commit=False)
    team.owner = owner
    team.save()

    TeamMembership.objects.create(
        team=team,
        user=owner,
        role=TeamMembership.Role.MANAGER,
    )

    return team


def join_team_by_code(user, code):
    team = Team.objects.filter(join_code=code).first()

    if not team:
        return None

    TeamMembership.objects.get_or_create(
        team=team,
        user=user,
        defaults={"role": TeamMembership.Role.EMPLOYEE},
    )

    return team
