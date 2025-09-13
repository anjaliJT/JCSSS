from django.db import models
from apps.complain_form.models import Event
from apps.users.models import CustomUser

from django.db import models
from django.utils import timezone

class CSMApproval(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="csm_approvals")

    def __str__(self):
        return f"{self.event.unique_token}"


class CSMApprovalHistory(models.Model):
    STATUS_CHOICES = [
        ("REVIEW", "Review"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("UNDER_PROCESS", "Under Process"),
        ("COMPLETED", "Completed"),
    ]

    LOCATION_CHOICES = [
        ("CUSTOMER_SITE", "Customer Site"),
        ("ON_SITE", "On Site"),
        ("COMPANY_SITE", "Company Site"),
    ]

    csm_approval = models.ForeignKey(CSMApproval, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="REVIEW")
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default="COMPANY_SITE")
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)  # auto timestamp

    def __str__(self):
        return f"{self.csm_approval.event.unique_token} - {self.status} at {self.updated_at.strftime('%Y-%m-%d %H:%M')}"


# class Team(models.Model):
#     # name = models.CharField(max_length=100)
#     department = models.CharField(max_length=100)  # e.g., "QA_QC"
#     members = models.ManyToManyField(CustomUser, related_name="teams")

#     def __str__(self):
#         return self.department


class ReviewReport(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="qaqc_reviews")
    # assigned_team = models.ManyToManyField(
    # Team,
    # related_name="qaqc_reviews",
    # blank=True )
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    department = models.CharField(max_length=250)
    assigned_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to="reports/", blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"QAQC Review for {self.event.unique_token}"
