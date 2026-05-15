from django import forms
from django.core.exceptions import ValidationError

from evaluations.models import Evaluation
from tasks.models import Task
from teams.permissions import is_team_manager, user_managed_team_ids


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ["task", "score"]

    def __init__(self, *args, evaluator=None, **kwargs):
        self.evaluator = evaluator
        super().__init__(*args, **kwargs)
        if evaluator is None:
            return

        evaluated_ids = Evaluation.objects.values_list("task_id", flat=True)

        self.fields["task"].queryset = Task.objects.filter(
            team_id__in=user_managed_team_ids(evaluator),
            status=Task.Status.DONE,
            assignee__isnull=False,
        ).exclude(id__in=evaluated_ids)

    def clean_task(self):
        task = self.cleaned_data["task"]
        if self.evaluator is None:
            return task

        if not is_team_manager(self.evaluator, task.team):
            raise ValidationError("Можно оценивать только задачи своих команд.")

        if Evaluation.objects.filter(task=task).exists():
            raise ValidationError("Эта задача уже оценена.")

        return task
