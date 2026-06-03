from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from teams.models import Team, TeamMembership

from .forms import RegisterForm


User = get_user_model()


class UserFormsTests(TestCase):
    def test_register_form_hashes_password(self):
        form = RegisterForm(
            data={
                "email": "new@example.com",
                "username": "newuser",
                "password": "pass12345",
            }
        )

        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertNotEqual(user.password, "pass12345")
        self.assertTrue(user.check_password("pass12345"))


class UserViewsTests(TestCase):
    def test_register_view_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "new@example.com",
                "username": "newuser",
                "password": "pass12345",
            },
        )

        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(email="new@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_user_list_shows_users_without_managed_team(self):
        user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="pass12345",
        )
        other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="pass12345",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("user_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.email)
        self.assertContains(response, other_user.email)

    def test_user_list_has_add_form_for_managed_team(self):
        manager = User.objects.create_user(
            email="manager@example.com",
            username="manager",
            password="pass12345",
        )
        employee = User.objects.create_user(
            email="employee@example.com",
            username="employee",
            password="pass12345",
        )
        team = Team.objects.create(name="Sales", owner=manager)
        TeamMembership.objects.create(
            team=team,
            user=manager,
            role=TeamMembership.Role.MANAGER,
        )
        self.client.force_login(manager)

        response = self.client.get(reverse("user_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, employee.email)
        self.assertContains(response, "Добавить в команду")
