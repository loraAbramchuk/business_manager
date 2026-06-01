from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from teams.permissions import is_team_manager, user_managed_team_ids

from .forms import EvaluationForm
from .models import Evaluation


@login_required
def evaluation_create_view(request):
    if not user_managed_team_ids(request.user).exists():
        return HttpResponseForbidden()

    if request.method == "POST":
        form = EvaluationForm(request.POST, evaluator=request.user)

        if form.is_valid():
            task = form.cleaned_data["task"]
            if not is_team_manager(request.user, task.team):
                return HttpResponseForbidden()

            evaluation = form.save(commit=False)
            evaluation.evaluator = request.user
            evaluation.employee = task.assignee
            evaluation.save()

            return redirect("my_evaluations")
    else:
        form = EvaluationForm(evaluator=request.user)

    return render(request, "evaluations/evaluation_form.html", {"form": form})


@login_required
def my_evaluations_view(request):
    evaluations = Evaluation.objects.filter(employee=request.user)

    today = timezone.now().date()

    year = request.GET.get("year", "").strip()
    month = request.GET.get("month", "").strip()

    y = None
    m = None
    avg = None
    period_error = ""
    has_custom_period = year != "" or month != ""

    if has_custom_period:
        if year == "" or month == "":
            period_error = "Введите и год, и месяц."
        else:
            try:
                y = int(year)
                m = int(month)
            except ValueError:
                period_error = "Год и месяц должны быть числами."

        if not period_error:
            if y < 1:
                period_error = "Год должен быть положительным числом."
            elif m < 1 or m > 12:
                period_error = "Месяц должен быть от 1 до 12."

    if period_error:
        avg_period_caption = "неверный период"
    elif has_custom_period:
        avg = request.user.average_score_for_month(y, m)
        avg_period_caption = f"{m:02d}.{y}"
    else:
        avg = request.user.average_score_for_current_month()
        avg_period_caption = f"текущий месяц ({today.month:02d}.{today.year})"

    return render(
        request,
        "evaluations/my_evaluations.html",
        {
            "evaluations": evaluations,
            "avg": avg,
            "filter_year": y,
            "filter_month": m,
            "avg_period_caption": avg_period_caption,
            "period_error": period_error,
        },
    )
