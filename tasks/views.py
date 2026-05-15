from datetime import date, timedelta

import calendar

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from meetings.models import Meeting
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from teams.permissions import (
    is_team_manager,
    user_managed_team_ids,
    user_team_ids,
)

from comments.forms import CommentForm
from .forms import TaskForm
from .models import Task
from .serializers import TaskSerializer


def _user_can_manage_task(user, task):
    if task.creator_id == user.id:
        return True
    return is_team_manager(user, task.team)


@login_required
def calendar_view(request):
    today = timezone.now().date()
    week = today + timedelta(days=7)
    team_ids = user_team_ids(request.user)
    tasks = Task.objects.filter(
        deadline__date__range=[today, week],
        team_id__in=team_ids,
    )
    meetings = (
        Meeting.objects.filter(start_time__date__range=[today, week])
        .filter(Q(organizer=request.user) | Q(participants=request.user))
        .distinct()
    )

    return render(
        request,
        "calendar.html",
        {
            "tasks": tasks,
            "meetings": meetings,
            "today": today,
        },
    )


@login_required
def task_list_view(request):
    tasks = Task.objects.filter(team_id__in=user_team_ids(request.user))

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "managed_team_ids": list(user_managed_team_ids(request.user)),
        },
    )


@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        team_id__in=user_team_ids(request.user),
    )

    comments = task.comments.select_related("author").order_by("created_at")

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()

            return redirect("task_detail", task_id=task.id)
    else:
        form = CommentForm()

    return render(
        request,
        "tasks/task_detail.html",
        {
            "task": task,
            "comments": comments,
            "form": form,
            "managed_team_ids": list(user_managed_team_ids(request.user)),
        },
    )


@login_required
def task_create_view(request):
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)

        if form.is_valid():
            team = form.cleaned_data["team"]
            if not is_team_manager(request.user, team):
                return HttpResponseForbidden()
            task = form.save(commit=False)
            task.creator = request.user
            task.save()

            return redirect("task_list")
    else:
        form = TaskForm(user=request.user)

    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def task_update_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not _user_can_manage_task(request.user, task):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, user=request.user)

        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def task_delete_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not _user_can_manage_task(request.user, task):
        return HttpResponseForbidden()

    task.delete()

    return redirect("task_list")


@login_required
def calendar_month_view(request):
    today = date.today()

    year = today.year
    month = today.month

    cal = calendar.Calendar(firstweekday=0)

    month_days = cal.monthdatescalendar(year, month)

    team_ids = user_team_ids(request.user)

    calendar_data = []
    for week in month_days:
        week_data = []

        for day in week:
            tasks = Task.objects.filter(deadline__date=day, team_id__in=team_ids)
            meetings = (
                Meeting.objects.filter(start_time__date=day)
                .filter(Q(organizer=request.user) | Q(participants=request.user))
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

    return render(
        request,
        "calendar_month.html",
        {
            "calendar_data": calendar_data,
            "month": month,
            "year": year,
            "today": today,
        },
    )


@login_required
def calendar_day_view(request, year, month, day):
    selected_date = date(year, month, day)
    team_ids = user_team_ids(request.user)

    tasks = Task.objects.filter(deadline__date=selected_date, team_id__in=team_ids)
    meetings = (
        Meeting.objects.filter(start_time__date=selected_date)
        .filter(Q(organizer=request.user) | Q(participants=request.user))
        .distinct()
    )

    return render(
        request,
        "calendar_day.html",
        {
            "date": selected_date,
            "tasks": tasks,
            "meetings": meetings,
        },
    )


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.none()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return Task.objects.filter(team_id__in=user_team_ids(user))

    def perform_create(self, serializer):
        team = serializer.validated_data.get("team")
        if not team or not is_team_manager(self.request.user, team):
            raise PermissionDenied("Только менеджер команды может создавать задачи.")
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        if not _user_can_manage_task(self.request.user, serializer.instance):
            raise PermissionDenied("Недостаточно прав для изменения задачи.")
        serializer.save()

    def perform_destroy(self, instance):
        if not _user_can_manage_task(self.request.user, instance):
            raise PermissionDenied("Недостаточно прав для удаления задачи.")
        instance.delete()
