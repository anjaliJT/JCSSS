

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from models import UAVType


class SparePartsRequest(models.Model):
    """
    Model for spare parts requests 
    """
    
    # Status Choices
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    DISPATCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
    ]
    
    AVAILABILITY_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    # Basic Information
    requested_by = models.CharField(max_length=100)
    unit_name = models.CharField(max_length=100)
    
    # Service Request (optional - link to existing service request)
    service_request = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Service request ID if applicable"
    )
    
    # UAV Details
    uav_type = models.ForeignKey(UAVType, max_length=100)
    tail_number = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    remarks = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)
    
    # Part Names (store as JSON array for multiple parts)
    part_names = models.JSONField(
        help_text="List of part names in JSON format"
    )
    
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
        choices=AVAILABILITY_STATUS_CHOICES,
        default='in_stock'
    )
    
    # Approval Status with datetime
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    approval_datetime = models.DateTimeField(null=True, blank=True)
    
    # Dispatch Status with datetime
    dispatch_status = models.CharField(
        max_length=20,
        choices=DISPATCH_STATUS_CHOICES,
        default='pending'
    )
    dispatch_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Spare Parts Request'
        verbose_name_plural = 'Spare Parts Requests'

    def __str__(self):
        return f"{self.tail_number} - {self.requested_by} - {self.created_at.strftime('%Y-%m-%d')}"

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

   