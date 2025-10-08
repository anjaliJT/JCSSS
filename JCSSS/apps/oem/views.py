from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import  CSMApprovalHistory, ReviewReport
from apps.complain_form.models import Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db import IntegrityError
from django.contrib import messages

class CSMViews(View):
    def get(self, request):
        # approvals = CSMApproval.objects.all().order_by("-id")  # latest first
        histories = CSMApprovalHistory.objects.all().order_by("-id")  # latest first

        return render(request, "csm/csm.html", {
            # "approvals": approvals,
            "histories": histories,
        })


    def post(self, request):
        approval_id = request.POST.get("approval_id")
        new_location = request.POST.get("location")
        new_status = request.POST.get("status")

        try:
            approval = CSMApprovalHistory.objects.get(id=approval_id)
            if new_location:
                approval.location = new_location
            if new_status:
                approval.status = new_status
            approval.save()

            # also log into history
            CSMApprovalHistory.objects.create(
            csm_approval=approval,   # ✅ correct field name
            location=new_location,
            status=new_status,
            remarks=request.POST.get("remarks", "")
        )

            # messages.success(request, "Approval updated successfully!")

        except CSMApproval.DoesNotExist:
            messages.error(request, "Approval not found.")

        return redirect("csm")  # redirect to same view (give name in urls.py)




@login_required
def submit_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        try:
            ReviewReport.objects.create(
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

