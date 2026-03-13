from django.db import models
from .complaint import UAVType
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError




class TrainingRequestStatus(models.TextChoices):
    pending = "pending", "Training Pending"
    inprogress = "in progress", "Training in progress"
    completed =  "completed", "Training Completed"


class TrainingType(models.TextChoices):
    REFRESHER = "refresher", "Refresher Training"
    INITIAL = "initial", "Initial Training"
    INSTRUCTOR = "instructor", "Instructor Training"
    CUSTOM = "custom", "Custom Training"


class LocationType(models.TextChoices):
    OEM = "oem", "OEM Facility"
    USER_SITE = "user_site", "User Site"
    OTHER = "other", "Other"


class TrainingRequest(models.Model):

    # service_request = models.OneToOneField(
    #     "service_requests.ServiceRequest",
    #     on_delete=models.CASCADE,
    #     related_name="training"
    # )

    # requester info
    requested_by = models.CharField(max_length=100)
    command_name = models.CharField(max_length=100)
    unit_name = models.CharField(max_length=200)
    uav_type = models.ForeignKey(UAVType, max_length=100, on_delete=models.PROTECT)
    number_of_participants = models.PositiveIntegerField(
    # participants
        validators=[MinValueValidator(10)]
    )

    # location
    preferred_location = models.CharField(
        max_length=20,
        choices=LocationType.choices
    )
    #location description for others 
    location_description = models.TextField()

    preferred_date = models.DateField()
    
    # Oem proposed date for training start date
    oem_proposed_date = models.DateField(
        blank=True,
        null=True
    )

    #total number of uavs in possession
    total_uavs = models.PositiveIntegerField()
    # tail number of possessed Total UAVs

    # training type
    training_type = models.CharField(
        max_length=20,
        choices=TrainingType.choices
    )

    #description required for customer training type 
    training_description = models.TextField()


    oem_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    training_request_status = models.CharField(max_length=250, choices=TrainingRequestStatus.choices)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):

        if (
            self.training_type == TrainingType.CUSTOM
            and not self.training_description
        ):
            raise ValidationError(
                "Custom training requires description"
            )

        if (
            self.preferred_location == LocationType.OTHER
            and not self.location_description
        ):
            raise ValidationError(
                "Location details required for 'Other'"
            )

    def __str__(self):
        return f"{self.requested_by} - {self.unit_name}"