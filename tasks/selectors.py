from datetime import date, timedelta

import calendar

from django.db.models import Q
from django.utils import timezone

from meetings.models import Meeting
from teams.permissions import user_team_ids

from .models import Task


def get_user_tasks(user):
    return Task.objects.filter(team_id__in=user_team_ids(user))


def get_week_calendar_data(user):
    today = timezone.now().date()
    week = today + timedelta(days=7)

    tasks = Task.objects.filter(
        deadline__date__range=[today, week],
        team_id__in=user_team_ids(user),
    )
    meetings = (
        Meeting.objects.filter(start_time__date__range=[today, week])
        .filter(Q(organizer=user) | Q(participants=user))
        .distinct()
    )

    return {
        "tasks": tasks,
        "meetings": meetings,
        "today": today,
    }


def get_day_calendar_data(user, selected_date):
    tasks = Task.objects.filter(
        deadline__date=selected_date,
        team_id__in=user_team_ids(user),
    )
    meetings = (
        Meeting.objects.filter(start_time__date=selected_date)
        .filter(Q(organizer=user) | Q(participants=user))
        .distinct()
    )

    return {
        "date": selected_date,
        "tasks": tasks,
        "meetings": meetings,
    }


def get_month_calendar_data(user):
    today = date.today()

    year = today.year
    month = today.month

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)
    team_ids = user_team_ids(user)

    calendar_data = []
    for week in month_days:
        week_data = []

        for day in week:
            tasks = Task.objects.filter(deadline__date=day, team_id__in=team_ids)
            meetings = (
                Meeting.objects.filter(start_time__date=day)
                .filter(Q(organizer=user) | Q(participants=user))
                .distinct()
            )

            week_data.append(
                {
                    "date": day,
                    "is_current_month": day.month == month,
                    "tasks": tasks,
                    "meetings": meetings,
                }
            )

        calendar_data.append(week_data)

    return {
        "calendar_data": calendar_data,
        "month": month,
        "year": year,
        "today": today,
    }
