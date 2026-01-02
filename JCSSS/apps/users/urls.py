# urls.py
from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('fetch/',  StatisticsView.as_view(), name='user-details'),
    path('', Login.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path("signup/",  SignupView.as_view(), name="signup"),
    path('profile/', profileView.as_view(),name="profile"),
    path('users/', UserManagementListView.as_view(), name='user_list'),
    path('users/create/', CreateOEMUserView.as_view(), name='create_oem_user'),
    path('users/<int:pk>/edit/', EditOEMUserView.as_view(), name='edit_oem_user'),
    path('users/<int:user_id>/permissions/', UserPermissionManagementView.as_view(), name='user_permissions'),
    path('forgot-password/', send_otp, name='forgot-password-send-otp'),
    path('verify-otp/',  verify_otp, name= 'forgot-password-verify'),
    
    path("send-otp/", send_email_otp, name="send_email_otp"),
    path("verify-email-otp/", verify_email_otp, name="verify_email_otp"),

    
    # path("404/", custom_404_view, name="page_not_found"), 
    # path("403/", custom_403_view, name="page_not_accessible"), 
    # path("500/", custom_500_view, name="page_went_wrong"), 
    
]