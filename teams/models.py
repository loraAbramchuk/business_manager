from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL

def generate_join_code():
    return str(uuid.uuid4())[:8]

class Team(models.Model):
    name = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_teams"
    )

    members = models.ManyToManyField(
        User,
        through="TeamMembership",
        related_name="teams"
    )

    join_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_join_code
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):

    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"],
                name="unique_team_membership",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.team} ({self.role})"
