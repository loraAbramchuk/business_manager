from django import forms
from django.contrib.auth import get_user_model

from .models import Team

User = get_user_model()


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    role = forms.ChoiceField(choices=[
        ("MANAGER", "Manager"),
        ("EMPLOYEE", "Employee"),
    ])

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]

class JoinTeamByCodeForm(forms.Form):
    code = forms.CharField(max_length=20, label="Team code")