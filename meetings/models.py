from django.db import models
from django.conf import settings
from teams.models import Team
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

class Meeting(models.Model):
    title = models.CharField(max_length=255)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_meetings"
    )

    participants = models.ManyToManyField(
        User,
        related_name="participant_meetings"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")

    def __str__(self):
        return self.title
