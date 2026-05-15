from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils import timezone

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        USER = "USER", "User"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length = 20,
        choices = Roles.choices,
        default=Roles.USER
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def average_score_for_month(self, year=None, month=None):
        """Средний балл за календарный месяц. По умолчанию — текущий месяц."""
        today = timezone.now().date()
        y = year if year is not None else today.year
        m = month if month is not None else today.month

        return self.received_evaluations.filter(
            created_at__year=y,
            created_at__month=m,
        ).aggregate(Avg("score"))["score__avg"]

    def average_score_for_current_month(self):
        today = timezone.now().date()
        return self.average_score_for_month(today.year, today.month)

    def __str__(self):
        return self.email

