from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAmin(admin.ModelAdmin):
    list_display = ("id", "title", "team", "organizer", "start_time", "end_time")
    filter_horizontal =  ("participants",)
