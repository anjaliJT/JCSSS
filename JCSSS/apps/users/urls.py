# urls.py
from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('fetch/',  UserDetails.as_view(), name='user-details'),
    path('', Login.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path("signup/",  SignupView.as_view(), name="signup"),
    path('profile/', profileView.as_view(),name="profile"),
    path('forgot-password/', send_otp, name='forgot-password-send-otp'),
    path('verify-otp/',  verify_otp, name= 'forgot-password-verify'),
]