from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from comments.services import create_comment
from teams.permissions import (
    is_team_manager,
    user_managed_team_ids,
    user_team_ids,
)

from comments.forms import CommentForm
from .forms import TaskForm
from .models import Task
from .permissions import can_manage_task
from .serializers import TaskSerializer
from .selectors import (
    get_day_calendar_data,
    get_month_calendar_data,
    get_user_tasks,
    get_week_calendar_data,
)
from .services import create_task, delete_task


@login_required
def calendar_view(request):
    calendar_data = get_week_calendar_data(request.user)
    return render(request, "calendar.html", calendar_data)


@login_required
def task_list_view(request):
    tasks = get_user_tasks(request.user)

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
            create_comment(form, task, request.user)

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
            create_task(form, request.user)

            return redirect("task_list")
    else:
        form = TaskForm(user=request.user)

    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def task_update_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not can_manage_task(request.user, task):
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

    if not can_manage_task(request.user, task):
        return HttpResponseForbidden()

    delete_task(task)

    return redirect("task_list")


@login_required
def calendar_month_view(request):
    calendar_data = get_month_calendar_data(request.user)
    return render(request, "calendar_month.html", calendar_data)


@login_required
def calendar_day_view(request, year, month, day):
    selected_date = date(year, month, day)
    calendar_data = get_day_calendar_data(request.user, selected_date)
    return render(request, "calendar_day.html", calendar_data)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.none()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return get_user_tasks(user)

    def perform_create(self, serializer):
        team = serializer.validated_data.get("team")
        if not team or not is_team_manager(self.request.user, team):
            raise PermissionDenied("Только менеджер команды может создавать задачи.")
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        if not can_manage_task(self.request.user, serializer.instance):
            raise PermissionDenied("Недостаточно прав для изменения задачи.")
        serializer.save()

    def perform_destroy(self, instance):
        if not can_manage_task(self.request.user, instance):
            raise PermissionDenied("Недостаточно прав для удаления задачи.")
        delete_task(instance)
