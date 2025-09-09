from django.urls import path
from apps.complain_form.views import *

urlpatterns = [
    path('fetch/', ComplaintRegister.as_view(), name='details'),
    path('submit/', ComplaintRegister.as_view(), name='submit'),
]