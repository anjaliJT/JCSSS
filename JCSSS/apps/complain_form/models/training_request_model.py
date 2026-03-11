from django.db import models
from models import UAVType
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

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

    service_request = models.OneToOneField(
        "service_requests.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="training"
    )

    # requester info
    requested_by = models.CharField(max_length=100)
    unit_name = models.CharField(max_length=200)
    command_name = models.CharField(max_length=100)

    # UAV info
    uav_type = models.ForeignKey(UAVType, max_length=100)
    total_uavs = models.PositiveIntegerField()

    # participants
    number_of_participants = models.PositiveIntegerField(
        validators=[MinValueValidator(10)]
    )

    # training type
    training_type = models.CharField(
        max_length=20,
        choices=TrainingType.choices
    )

    custom_training_description = models.TextField(
        blank=True
    )

    # location
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices
    )

    location_details = models.CharField(
        max_length=200,
        blank=True
    )

    preferred_date = models.DateField()

    description_of_requirements = models.TextField()

    # OEM details
    oem_proposed_date = models.DateField(
        blank=True,
        null=True
    )

    oem_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):

        if (
            self.training_type == TrainingType.CUSTOM
            and not self.custom_training_description
        ):
            raise ValidationError(
                "Custom training requires description"
            )

        if (
            self.location_type == LocationType.OTHER
            and not self.location_details
        ):
            raise ValidationError(
                "Location details required for 'Other'"
            )

    def __str__(self):
        return f"{self.service_request.request_number} - {self.unit_name}"