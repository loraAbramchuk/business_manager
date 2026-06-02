from django.utils import timezone


def create_evaluation(form, evaluator):
    task = form.cleaned_data["task"]

    evaluation = form.save(commit=False)
    evaluation.evaluator = evaluator
    evaluation.employee = task.assignee
    evaluation.save()

    return evaluation


def get_average_score_data(user, year, month):
    today = timezone.now().date()

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
        avg = user.average_score_for_month(y, m)
        avg_period_caption = f"{m:02d}.{y}"
    else:
        avg = user.average_score_for_current_month()
        avg_period_caption = f"текущий месяц ({today.month:02d}.{today.year})"

    return {
        "avg": avg,
        "filter_year": y,
        "filter_month": m,
        "avg_period_caption": avg_period_caption,
        "period_error": period_error,
    }
