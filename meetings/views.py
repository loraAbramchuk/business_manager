from django.contrib import messages
from django.db import DatabaseError, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from .forms import MeetingForm
from .models import Meeting


@login_required
def meeting_list_view(request):
    meetings = Meeting.objects.filter(participants=request.user)

    return render(request, "meetings/meeting_list.html", {
        "meetings": meetings
    })


@login_required
def meeting_create_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)

        if form.is_valid():
            try:
                meeting = form.save(commit=False)
                meeting.organizer = request.user
                meeting.save()
                form.save_m2m()
                meeting.participants.add(request.user)
                return redirect("meeting_list")
            except (DatabaseError, IntegrityError):
                messages.error(request, "Не удалось создать встречу.")
    else:
        form = MeetingForm()

    return render(request, "meetings/meeting_form.html", {"form": form})


@login_required
@require_POST
def meeting_delete_view(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    if request.user != meeting.organizer and not meeting.participants.filter(
        pk=request.user.pk
    ).exists():
        return HttpResponseForbidden()

    try:
        meeting.delete()
    except (DatabaseError, IntegrityError):
        messages.error(request, "Не удалось удалить встречу.")

    return redirect("meeting_list")
