from .models import Evaluation


def get_evaluations_for_user(user):
    return Evaluation.objects.filter(employee=user)
