#   # Status Choices
    # APPROVAL_STATUS_CHOICES = [
    #     ('pending', 'Pending'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    # ]
    
#     DISPATCH_STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('complete', 'Complete'),
#     ]
    
#     AVAILABILITY_STATUS_CHOICES = [
#         ('in_stock', 'In Stock'),
#         ('out_of_stock', 'Out of Stock'),
#     ]


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .complaint import UAVType

"""
model wise item lists 
common parts lists
"""
class Items(models.Model):
   uav_type = models.ForeignKey(UAVType,on_delete=models.PROTECT, related_name="items")
   items_name = models.CharField(max_length=250)
   created_at = models.DateField(auto_now_add=True,blank=True, null=True)

   class Meta:
       unique_together = ["uav_type","items_name"] 
       # prevent dublicate like : [("jm1","battery"),("jm1","battery")]

   def __str__(self):
       return f"{self.items_name} ({self.uav_type})"

class SparePartsRequest(models.Model):
    """
    Model for spare parts requests 
    """  
    # Basic Information
    requested_by = models.CharField(max_length=100)
    unit_name = models.CharField(max_length=100)
    # service_request_id  if exist
    service_request_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Service request ID if applicable"
    )
    
    # UAV Details
    uav_type = models.ForeignKey(UAVType, max_length=100, on_delete=models.PROTECT)
    tail_number = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.unit_name} - {self.uav_type}"

class SparePartRequestItems(models.Model):
    request = models.ForeignKey(SparePartsRequest,on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Items,on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
  
    # Cost Information
    oem_actual_cost = models.DecimalField(max_digits=10, decimal_places=2)

    gst = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    cost_for_customer = models.DecimalField(max_digits=10, decimal_places=2)
    
 
    # Profit Margin (calculated field)
    profit_margin = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        editable=False,
        default=0
    )
    
    # Status Fields
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('in_stock', 'In Stock'),
            ('out_of_stock', 'Out of Stock'),
        ],
        default='in_stock'
    )
    
    # Approval Status with datetime
    approval_status = models.CharField(
        max_length=20,
        choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ],
        default='pending'
    )
    approval_datetime = models.DateTimeField(null=True, blank=True)
    
    # Dispatch Status with datetime
    dispatch_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'),
            ('complete', 'Complete'),
        ],
        default='pending'
    )
    dispatch_datetime = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate profit margin before saving
        if self.oem_actual_cost and self.oem_actual_cost > 0:
            margin = ((self.cost_for_customer - self.oem_actual_cost) / self.oem_actual_cost) * 100
            self.profit_margin = round(margin, 2)
        
        # Auto-set approval datetime when status changes
        if self.approval_status in ['approved', 'rejected'] and not self.approval_datetime:
            self.approval_datetime = timezone.now()
        
        # Auto-set dispatch datetime when status changes to complete
        if self.dispatch_status == 'complete' and not self.dispatch_datetime:
            self.dispatch_datetime = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item},{self.quantity}"

   