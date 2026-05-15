from django import forms
from django.core.exceptions import ValidationError

from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["title", "team", "participants", "start_time", "end_time"]

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            )
        }

    def clean(self):
        cleaned_data = super().clean()

        participants = cleaned_data.get("participants")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if not participants or not start or not end:
            return cleaned_data

        for user in participants:
            overlapping = Meeting.objects.filter(
                participants=user,
                start_time__lt=end,
                end_time__gt=start,
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise ValidationError(f"{user} уже занят в это время")

        return cleaned_data