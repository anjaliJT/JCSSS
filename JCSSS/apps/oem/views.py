from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import  ComplaintStatus
from apps.complain_form.models import Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db import IntegrityError
from django.contrib import messages



@login_required
def submit_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        try:
            ComplaintStatus.objects.create(
                event=event,
                assigned_team=request.POST.get("assigned_team"),
                user=request.user,
                department=request.POST.get("department"),
                report_file=request.FILES.get("report_file"),
                submitted_at=now(),
                remarks=request.POST.get("remarks"),
            )
            messages.success(request, " Review submitted successfully!")
        except IntegrityError:
            messages.warning(request, "You have already submitted a report for this complain.")

        return redirect("complaint_list")  # or use namespace if you have one

    # If GET request, just redirect back or handle as needed
    return redirect("complaint_list")