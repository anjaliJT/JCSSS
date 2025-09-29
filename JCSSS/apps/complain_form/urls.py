from django.urls import path
from apps.complain_form.views import ComplaintRegister, ComplaintListView, ComplaintDetailView

# app_name = "complaints"

urlpatterns = [
    path('submit/', ComplaintRegister.as_view(), name='complain_submit'),  # Submit new complaint
    path('fetch/', ComplaintRegister.as_view(), name='complain_detail'),  # Keeping for backward compatibility
    path("complain/list/", ComplaintListView.as_view(), name="complaint_list"),
    path("complain/<int:pk>/", ComplaintDetailView.as_view(), name="complaint_detail"),
]