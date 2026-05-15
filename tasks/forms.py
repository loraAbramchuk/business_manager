from django import forms

from teams.models import Team, TeamMembership

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "team", "assignee", "deadline", "status"]

        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            )
        }

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        if user is None:
            return

        managed = Team.objects.filter(
            teammembership__user=user,
            teammembership__role=TeamMembership.Role.MANAGER,
        ).distinct()

        if self.instance.pk and self.instance.team_id:
            self.fields["team"].queryset = (
                managed | Team.objects.filter(pk=self.instance.team_id)
            ).distinct()
        else:
            self.fields["team"].queryset = managed
