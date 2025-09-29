from django.db import models
import uuid
import hashlib

from datetime import datetime
from django.db import models
from apps.users.models import CustomUser
class Event(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in-progress', 'In Progress'),
        ('awaiting-parts', 'Awaiting Parts'),
        ('resolved', 'Resolved'),
    )
    
    unique_token = models.CharField(max_length=100, unique=True, blank=True)
    pilot_name = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    filed_by = models.CharField(max_length=250, blank=True, null=True)
    designation = models.CharField(max_length=150, blank=True, null=True)
    model_number = models.CharField(max_length=50)
    date_of_occurrence = models.DateField(blank=True)
    time_of_occurrence = models.TimeField(blank=True)
    field_site = models.CharField(max_length=250, blank=True)
    event_type = models.CharField(max_length=50, blank=True)
    damage_level = models.CharField(max_length=50, blank=True)
    flight_mode = models.CharField(max_length=50, blank=True)
    event_phase = models.CharField(max_length=50, blank=True)
    uav_type = models.CharField(max_length=150, blank=True)
    tail_number = models.CharField(max_length=50, blank=True)
    gcs_type = models.CharField(max_length=100, blank=True)
    gcs_number = models.CharField(max_length=50, blank=True)
    uav_weight = models.FloatField(help_text="Weight in kg")
    event_description = models.TextField(blank=True)
    initial_actions_taken = models.TextField(blank=True)
    remarks = models.TextField(blank=True, null=True)
    organization = models.CharField(max_length=200)
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.date_of_occurrence} ({self.pilot_name})"
    

    def save(self, *args, **kwargs):
        # Always store model_number in uppercase
        if self.model_number:
            self.model_number = self.model_number.upper()

        # First save to get the ID
        super().save(*args, **kwargs)

        # Generate unique_token only if not set
        if not self.unique_token:
            # Ensure date_of_occurrence is a date object
            if isinstance(self.date_of_occurrence, str):
                self.date_of_occurrence = datetime.strptime(self.date_of_occurrence, "%Y-%m-%d").date()

            # Count how many events already exist for this model
            count = Event.objects.filter(model_number=self.model_number).count()

            # Use next serial number (count is including current, so it's correct)
            serial_number = str(count).zfill(4)  # 0001, 0002, etc.

            # Build unique token
            self.unique_token = (
                f"0{self.id}-{self.model_number}-"
                f"{self.reported_at.strftime('%Y%m%d')}-{serial_number}".upper()
            )

            # Save again only for unique_token
            super().save(update_fields=["unique_token"])

class Meteorology(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT
    )
    wind = models.CharField(max_length=100, help_text="Wind condition")
    temperature = models.CharField(max_length=50, help_text="Temperature")
    pressure_qnh = models.CharField(max_length=50, help_text="QNH Pressure")
    # visibility = models.CharField(max_length=100, blank=True)
    # clouds = models.CharField(max_length=100, blank=True)
    # humidity = models.CharField(max_length=50, blank=True)
    turbulence = models.BooleanField(default=False)
    windshear = models.BooleanField(default=False)
    rain = models.BooleanField(default=False)
    icing = models.BooleanField(default=False)
    snow = models.BooleanField(default=False)

    def __str__(self):
        return f"Wind: {self.wind}, Temp: {self.temperature}"

class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="attachments"
    )
    file_video = models.FileField(upload_to="attachments/",blank=True)
    file_image1 = models.FileField(upload_to="attachments/",blank=True)
    file_image2 = models.FileField(upload_to="attachments/",blank=True)
    file_image3 = models.FileField(upload_to="attachments/", blank=True)
    file_log = models.FileField(upload_to="log/", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.event}"

class EventSeverityClassification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.OneToOneField(
        Event, on_delete=models.PROTECT, related_name="severity_classification"
    )
    damage_potential = models.CharField(
        max_length=20, choices=[("Minor", "Minor"), ("Moderate", "Moderate"), ("Severe", "Severe")]
    )
    # incident_severity = models.CharField(
    #     max_length=20, choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")]
    # )

    def __str__(self):
        return f"{self.event}"
