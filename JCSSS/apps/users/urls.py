# urls.py
from django.urls import path
from apps.users import views

urlpatterns = [
    path('fetch/', views.UserDetails.as_view(), name='user-details'),
    path('login/',views.Login.as_view(), name="login"),
    path('logout/',views.logout_view, name="logout"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path('profile/',views.profileView.as_view(),name="profile"),
]