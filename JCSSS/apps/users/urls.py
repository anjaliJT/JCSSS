# urls.py
from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('fetch/', UserDetails.as_view(), name='user-details'),
    path('fetch-dummy/', UserDetails_dummy.as_view(), name='user-details-dummy'),
    path('login/',Login.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
]

