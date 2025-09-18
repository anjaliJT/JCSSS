from django.urls import path
from apps.complain_form.views import *

urlpatterns = [
    path('fetch/', ComplaintRegister.as_view(), name='complain_details'),
    path('submit/', ComplaintRegister.as_view(), name='complain_submit'),
    path('fetch-dummy/', UserDetails_dummy.as_view(), name='user-details-dummy'),
    
]