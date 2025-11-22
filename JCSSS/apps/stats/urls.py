# statistics/urls.py
from django.urls import path
from .views import StatisticsView

urlpatterns = [
    path('fetch/',  StatisticsView.as_view(), name='user-details'),
    
]
