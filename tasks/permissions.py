from teams.permissions import is_team_manager


def can_manage_task(user, task):
    if task.creator_id == user.id:
        return True
    return is_team_manager(user, task.team)
