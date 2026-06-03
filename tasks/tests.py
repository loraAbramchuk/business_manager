from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from comments.models import Comment
from teams.models import Team, TeamMembership

from .forms import TaskForm
from .models import Task
from .permissions import can_manage_task
from .services import create_task


User = get_user_model()


class TaskBaseTestCase(TestCase):
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


class TaskServicesTests(TaskBaseTestCase):
    def test_create_task_sets_creator(self):
        form = TaskForm(
            data={
                "title": "Call client",
                "description": "Discuss contract",
                "team": self.team.id,
                "assignee": self.employee.id,
                "status": Task.Status.OPEN,
            },
            user=self.manager,
        )

        self.assertTrue(form.is_valid())
        task = create_task(form, self.manager)

        self.assertEqual(task.creator, self.manager)
        self.assertEqual(task.assignee, self.employee)
        self.assertEqual(task.team, self.team)

    def test_can_manage_task_for_creator_and_manager_only(self):
        task = Task.objects.create(
            title="Call client",
            team=self.team,
            assignee=self.employee,
            creator=self.manager,
        )

        self.assertTrue(can_manage_task(self.manager, task))
        self.assertFalse(can_manage_task(self.employee, task))
        self.assertFalse(can_manage_task(self.outsider, task))


class TaskViewsTests(TaskBaseTestCase):
    def test_manager_can_create_task(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("task_create"),
            {
                "title": "Call client",
                "description": "Discuss contract",
                "team": self.team.id,
                "assignee": self.employee.id,
                "status": Task.Status.OPEN,
            },
        )

        self.assertRedirects(response, reverse("task_list"))
        self.assertTrue(Task.objects.filter(title="Call client").exists())

    def test_employee_cannot_create_task(self):
        self.client.force_login(self.employee)

        response = self.client.post(
            reverse("task_create"),
            {
                "title": "Call client",
                "description": "Discuss contract",
                "team": self.team.id,
                "assignee": self.employee.id,
                "status": Task.Status.OPEN,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(title="Call client").exists())

    def test_member_can_add_comment_to_task(self):
        task = Task.objects.create(
            title="Call client",
            team=self.team,
            assignee=self.employee,
            creator=self.manager,
        )
        self.client.force_login(self.employee)

        response = self.client.post(
            reverse("task_detail", args=[task.id]),
            {"text": "Done"},
        )

        self.assertRedirects(response, reverse("task_detail", args=[task.id]))
        self.assertTrue(
            Comment.objects.filter(task=task, author=self.employee, text="Done").exists()
        )

    def test_outsider_cannot_open_task_detail(self):
        task = Task.objects.create(
            title="Call client",
            team=self.team,
            assignee=self.employee,
            creator=self.manager,
        )
        self.client.force_login(self.outsider)

        response = self.client.get(reverse("task_detail", args=[task.id]))

        self.assertEqual(response.status_code, 404)


class TaskApiTests(TaskBaseTestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_api_lists_only_user_team_tasks(self):
        own_task = Task.objects.create(
            title="Own task",
            team=self.team,
            assignee=self.employee,
            creator=self.manager,
        )
        other_team = Team.objects.create(name="Other", owner=self.outsider)
        Task.objects.create(
            title="Hidden task",
            team=other_team,
            assignee=self.outsider,
            creator=self.outsider,
        )
        self.api_client.force_authenticate(user=self.employee)

        response = self.api_client.get("/api/tasks/")

        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.data]
        self.assertIn(own_task.title, titles)
        self.assertNotIn("Hidden task", titles)

    def test_api_manager_can_create_task(self):
        self.api_client.force_authenticate(user=self.manager)

        response = self.api_client.post(
            "/api/tasks/",
            {
                "title": "API task",
                "description": "",
                "team": self.team.id,
                "assignee": self.employee.id,
                "status": Task.Status.OPEN,
            },
        )

        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(title="API task")
        self.assertEqual(task.creator, self.manager)

    def test_api_employee_cannot_create_task(self):
        self.api_client.force_authenticate(user=self.employee)

        response = self.api_client.post(
            "/api/tasks/",
            {
                "title": "API task",
                "description": "",
                "team": self.team.id,
                "assignee": self.employee.id,
                "status": Task.Status.OPEN,
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Task.objects.filter(title="API task").exists())
