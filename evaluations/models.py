from django.db import models
from django.conf import settings
from tasks.models import Task
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL

class Evaluation(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="evaluations"
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_evaluations"
    )

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="given_evaluations"
    )

    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["task"], name="unique_task_evaluation"),
        ]

    def __str__(self):
        return f"{self.employee} - {self.score}"
