from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from teams.permissions import is_team_manager, user_managed_team_ids

from .forms import EvaluationForm
from .selectors import get_evaluations_for_user
from .services import create_evaluation, get_average_score_data


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

            create_evaluation(form, request.user)

            return redirect("my_evaluations")
    else:
        form = EvaluationForm(evaluator=request.user)

    return render(request, "evaluations/evaluation_form.html", {"form": form})


@login_required
def my_evaluations_view(request):
    evaluations = get_evaluations_for_user(request.user)

    year = request.GET.get("year", "").strip()
    month = request.GET.get("month", "").strip()
    average_data = get_average_score_data(request.user, year, month)

    return render(
        request,
        "evaluations/my_evaluations.html",
        {
            "evaluations": evaluations,
            **average_data,
        },
    )
