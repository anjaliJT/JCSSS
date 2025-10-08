from django.contrib import admin
from apps.users.models import CustomUser, ForgotPasswordOTP

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ForgotPasswordOTP)