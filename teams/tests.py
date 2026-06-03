from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import TeamForm
from .models import Team, TeamMembership
from .permissions import is_team_manager, is_team_member
from .services import add_or_update_member, create_team, join_team_by_code


User = get_user_model()


class TeamServicesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="pass12345",
        )
        self.employee = User.objects.create_user(
            email="employee@example.com",
            username="employee",
            password="pass12345",
        )

    def test_create_team_adds_owner_as_manager(self):
        form = TeamForm(data={"name": "Sales"})

        self.assertTrue(form.is_valid())
        team = create_team(form, self.owner)

        self.assertEqual(team.owner, self.owner)
        self.assertTrue(is_team_member(self.owner, team))
        self.assertTrue(is_team_manager(self.owner, team))

    def test_add_or_update_member_updates_existing_role(self):
        team = Team.objects.create(name="Sales", owner=self.owner)

        membership, created = add_or_update_member(
            team,
            self.employee,
            TeamMembership.Role.EMPLOYEE,
        )
        self.assertTrue(created)
        self.assertEqual(membership.role, TeamMembership.Role.EMPLOYEE)

        membership, created = add_or_update_member(
            team,
            self.employee,
            TeamMembership.Role.MANAGER,
        )
        membership.refresh_from_db()

        self.assertFalse(created)
        self.assertEqual(membership.role, TeamMembership.Role.MANAGER)
        self.assertEqual(TeamMembership.objects.filter(team=team).count(), 1)

    def test_join_team_by_code_adds_employee(self):
        team = Team.objects.create(name="Sales", owner=self.owner)

        joined_team = join_team_by_code(self.employee, team.join_code)

        self.assertEqual(joined_team, team)
        membership = TeamMembership.objects.get(team=team, user=self.employee)
        self.assertEqual(membership.role, TeamMembership.Role.EMPLOYEE)

    def test_join_team_by_wrong_code_returns_none(self):
        result = join_team_by_code(self.employee, "wrong-code")

        self.assertIsNone(result)


class TeamViewsTests(TestCase):
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
        self.team = Team.objects.create(name="Sales", owner=self.manager)
        TeamMembership.objects.create(
            team=self.team,
            user=self.manager,
            role=TeamMembership.Role.MANAGER,
        )

    def test_manager_can_open_team_detail(self):
        self.client.force_login(self.manager)

        response = self.client.get(reverse("team_detail", args=[self.team.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sales")

    def test_non_member_cannot_open_team_detail(self):
        self.client.force_login(self.employee)

        response = self.client.get(reverse("team_detail", args=[self.team.id]))

        self.assertEqual(response.status_code, 403)

    def test_manager_can_quick_add_member(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("quick_add_member"),
            {
                "user_id": self.employee.id,
                "team_id": self.team.id,
                "role": TeamMembership.Role.EMPLOYEE,
            },
        )

        self.assertRedirects(response, reverse("user_list"))
        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.employee,
                role=TeamMembership.Role.EMPLOYEE,
            ).exists()
        )
