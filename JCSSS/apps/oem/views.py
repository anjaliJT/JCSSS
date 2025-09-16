from django.shortcuts import render, redirect
from django.views import View
from .models import CSMApproval, CSMApprovalHistory
from django.contrib import messages

class CSMViews(View):
    def get(self, request):
        approvals = CSMApproval.objects.all().order_by("-id")  # latest first
        histories = CSMApprovalHistory.objects.all().order_by("-id")  # latest first

        return render(request, "csm/csm.html", {
            "approvals": approvals,
            "histories": histories,
        })


    def post(self, request):
        approval_id = request.POST.get("approval_id")
        new_location = request.POST.get("location")
        new_status = request.POST.get("status")

        try:
            approval = CSMApproval.objects.get(id=approval_id)
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
