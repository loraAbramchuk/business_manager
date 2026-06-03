from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task
from teams.models import Team, TeamMembership

from .forms import EvaluationForm
from .models import Evaluation
from .services import get_average_score_data


User = get_user_model()


class EvaluationBaseTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            username="manager",
            password="pass12345",
        )
        self.employee = User.objects.create_user(
            email="employee@example.com",
            username="employee",
            password="pass12345",
        )
        self.outsider = User.objects.create_user(
            email="outsider@example.com",
            username="outsider",
            password="pass12345",
        )
        self.team = Team.objects.create(name="Sales", owner=self.manager)
        TeamMembership.objects.create(
            team=self.team,
            user=self.manager,
            role=TeamMembership.Role.MANAGER,
        )
        TeamMembership.objects.create(
            team=self.team,
            user=self.employee,
            role=TeamMembership.Role.EMPLOYEE,
        )
        self.done_task = Task.objects.create(
            title="Done task",
            team=self.team,
            assignee=self.employee,
            creator=self.manager,
            status=Task.Status.DONE,
        )


class EvaluationServicesTests(EvaluationBaseTestCase):
    def test_average_score_data_rejects_text_period(self):
        data = get_average_score_data(self.employee, "abc", "5")

        self.assertEqual(data["period_error"], "Год и месяц должны быть числами.")
        self.assertEqual(data["avg_period_caption"], "неверный период")
        self.assertIsNone(data["avg"])

    def test_average_score_data_rejects_wrong_month(self):
        data = get_average_score_data(self.employee, "2026", "13")

        self.assertEqual(data["period_error"], "Месяц должен быть от 1 до 12.")
        self.assertEqual(data["avg_period_caption"], "неверный период")

    def test_average_score_data_requires_year_and_month_together(self):
        data = get_average_score_data(self.employee, "2026", "")

        self.assertEqual(data["period_error"], "Введите и год, и месяц.")


class EvaluationFormTests(EvaluationBaseTestCase):
    def test_form_shows_done_tasks_for_manager(self):
        form = EvaluationForm(evaluator=self.manager)

        self.assertIn(self.done_task, form.fields["task"].queryset)

    def test_form_does_not_show_open_tasks(self):
        open_task = Task.objects.create(
            title="Open task",
            team=self.team,
            assignee=self.employee,
            creator=self.manager,
            status=Task.Status.OPEN,
        )

        form = EvaluationForm(evaluator=self.manager)

        self.assertNotIn(open_task, form.fields["task"].queryset)

    def test_form_does_not_show_already_evaluated_task(self):
        Evaluation.objects.create(
            task=self.done_task,
            employee=self.employee,
            evaluator=self.manager,
            score=5,
        )

        form = EvaluationForm(evaluator=self.manager)

        self.assertNotIn(self.done_task, form.fields["task"].queryset)


class EvaluationViewsTests(EvaluationBaseTestCase):
    def test_manager_can_create_evaluation(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("evaluation_create"),
            {
                "task": self.done_task.id,
                "score": 5,
            },
        )

        self.assertRedirects(response, reverse("my_evaluations"))
        evaluation = Evaluation.objects.get(task=self.done_task)
        self.assertEqual(evaluation.employee, self.employee)
        self.assertEqual(evaluation.evaluator, self.manager)

    def test_employee_cannot_open_evaluation_create_page(self):
        self.client.force_login(self.employee)

        response = self.client.get(reverse("evaluation_create"))

        self.assertEqual(response.status_code, 403)

    def test_my_evaluations_view_shows_period_error(self):
        self.client.force_login(self.employee)

        response = self.client.get(
            reverse("my_evaluations"),
            {"year": "abc", "month": "5"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Год и месяц должны быть числами.")
        self.assertContains(response, "неверный период")
