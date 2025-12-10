
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


class RepairLocation(models.Model):  
    LOCATION_CHOICES = [
        ("OEM Site", "OEM Site"),
        ("Customer Site", "Customer Site"),
        ("Virtual Assistance", "Virtual Assistance"),
    ]

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="location")
    location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        default="OEM Site"
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.event)



class ComplaintStatus(models.Model):
    STATUS_CHOICES = [
        ("IN REVIEW", "In Review"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("PRODUCT_RECEIVED", "Product Received"),
        ("DIAGNOSIS", "Diagnosis"),
        ("REPAIR", "Repair"),
        ("READY FOR DISPATCH", "Ready for Dispatch"),
        ("CLOSED", "Closed"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="complaint_statuses")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="REVIEW")
    remarks = models.TextField(blank=True, null=True)
    attachments = models.FileField(upload_to="attachments/", blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(CustomUser, on_delete= models.PROTECT,null=True, blank=True)

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
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Customer Price for {self.event}: ₹{self.total_price}"



