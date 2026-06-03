from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from teams.models import Team, TeamMembership

from .forms import MeetingForm
from .models import Meeting


User = get_user_model()


class MeetingBaseTestCase(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            username="organizer",
            password="pass12345",
        )
        self.participant = User.objects.create_user(
            email="participant@example.com",
            username="participant",
            password="pass12345",
        )
        self.outsider = User.objects.create_user(
            email="outsider@example.com",
            username="outsider",
            password="pass12345",
        )
        self.team = Team.objects.create(name="Sales", owner=self.organizer)
        TeamMembership.objects.create(
            team=self.team,
            user=self.organizer,
            role=TeamMembership.Role.MANAGER,
        )


class MeetingFormTests(MeetingBaseTestCase):
    def test_form_rejects_overlapping_meeting(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        meeting = Meeting.objects.create(
            title="First meeting",
            team=self.team,
            organizer=self.organizer,
            start_time=start,
            end_time=end,
        )
        meeting.participants.add(self.participant)

        form = MeetingForm(
            data={
                "title": "Second meeting",
                "team": self.team.id,
                "participants": [self.participant.id],
                "start_time": (start + timedelta(minutes=10)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "end_time": (end + timedelta(minutes=10)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("уже занят", str(form.errors))


class MeetingViewsTests(MeetingBaseTestCase):
    def test_create_meeting_adds_organizer_as_participant(self):
        self.client.force_login(self.organizer)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)

        response = self.client.post(
            reverse("meeting_create"),
            {
                "title": "Planning",
                "team": self.team.id,
                "participants": [self.participant.id],
                "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

        self.assertRedirects(response, reverse("meeting_list"))
        meeting = Meeting.objects.get(title="Planning")
        self.assertTrue(meeting.participants.filter(id=self.organizer.id).exists())
        self.assertTrue(meeting.participants.filter(id=self.participant.id).exists())

    def test_participant_can_delete_meeting(self):
        meeting = Meeting.objects.create(
            title="Planning",
            team=self.team,
            organizer=self.organizer,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
        )
        meeting.participants.add(self.participant)
        self.client.force_login(self.participant)

        response = self.client.post(reverse("meeting_delete", args=[meeting.id]))

        self.assertRedirects(response, reverse("meeting_list"))
        self.assertFalse(Meeting.objects.filter(id=meeting.id).exists())

    def test_outsider_cannot_delete_meeting(self):
        meeting = Meeting.objects.create(
            title="Planning",
            team=self.team,
            organizer=self.organizer,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
        )
        self.client.force_login(self.outsider)

        response = self.client.post(reverse("meeting_delete", args=[meeting.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Meeting.objects.filter(id=meeting.id).exists())
