
"""
Data models : 
RepairLocation 
ComplainStatus
RepairActualCost
RepairCostToCustomer 

Functions: 
Calculate : Profit-margin 
Calculate : Delayed or on time repair with timestamp 
    Logic : After verification : the timestamp  will be noted the diagnosis or payment should sent withing 3 days (72 hours)
            if cross 72 hours : mark delay

SendMail : for each staus mail will be sent to all stakeholders

TO DO : 
change manufecturer site to --> OEM Site 
Virtual  to --> Online Support 

each model should have: 
    i) Created_at
    ii) Created_by  fields.

"""


from django.db import models
from apps.complain_form.models import Event
from apps.users.models import CustomUser

from django.db import models
from django.utils import timezone


class Location(models.Model): # Rename it - > RepairLocation 
    LOCATION_CHOICES = [
        ("OEM_SITE", "OEM Site"),
        ("CUSTOMER_SITE", "Customer Site"),
        ("VIRTUAL_ASSISTANCE", "Virtual Assistance"),
    ]

    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="locations")
    location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        default="MANUFACTURER_SITE"
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.event}"


class ComplaintStatus(models.Model):
    STATUS_CHOICES = [
        ("REVIEW", "Review"),
        ("ACCEPTED", "Accepted"),
        ("DIAGNOSIS", "Diagnosis"),
        ("REPAIR", "Repair"),
        ("REJECTED", "Rejected"),
        ("READY FOR DISPATCH", "Ready for Dispatch"),
        ("CLOSED", "Closed"),
    ]

    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="complaint_statuses")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="REVIEW")
    remarks = models.TextField(blank=True, null=True)
    attachments = models.FileField(upload_to="attachments/", blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.event} - {self.get_status_display()} ({self.updated_at.strftime('%Y-%m-%d %H:%M')})"


class RepairCost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="repair_costs")
    description = models.TextField(blank=True, null=True)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2)
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repair Cost for {self.event}: ₹{self.repair_cost}"


class CustomerPricing(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="customer_pricing")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    invoice = models.FileField(upload_to="attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Customer Price for {self.event}: ₹{self.total_price}"


