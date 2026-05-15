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

    year = request.GET.get("year")
    month = request.GET.get("month")
    try:
        y = int(year) if year is not None else None
        m = int(month) if month is not None else None
    except ValueError:
        y, m = None, None

    avg = request.user.average_score_for_month(y, m)

    today = timezone.now().date()
    gy, gm = request.GET.get("year"), request.GET.get("month")
    has_custom_period = bool(
        (gy is not None and str(gy).strip() != "")
        or (gm is not None and str(gm).strip() != "")
    )
    if has_custom_period and y is not None and m is not None:
        avg_period_caption = f"{m:02d}.{y}"
    else:
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
        },
    )
