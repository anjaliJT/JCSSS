# urls.py
from django.urls import path
from apps.users import views

urlpatterns = [
    path('fetch/', views.UserDetails.as_view(), name='user-details'),
    path('fetch-dummy/', views.UserDetails_dummy.as_view(), name='user-details-dummy'),
    path('login/',views.Login.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path('profile/',views.profileView.as_view(),name="profile"),
]

