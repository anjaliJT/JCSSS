from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

from django.core.validators import RegexValidator
phone_regex = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be 10 digits"
)

# Create your models here.
class CustomUser(AbstractUser):
    """Custom user model extending AbstractUser.
    - email: Email field, unique for each user.
    - designation: Designation of the user.
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    certificate_number = models.CharField(max_length= 250, unique=True, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    command_name = models.CharField(max_length=250, blank=True, null=True)
    username = None
    
    ROLE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("CSM", "CSM"),
        ("DIRECTOR", "Director"),
        ("EMPLOYEE", "Employee"),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='CUSTOMER')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.first_name}, {self.last_name} - {self.email}"