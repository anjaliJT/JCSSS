from django.urls import path
from apps.complain_form.views import ComplaintRegister, ComplaintListView

urlpatterns = [
    path('', ComplaintListView.as_view(), name='complaint-list'),  # Main complaints page
    path('submit/', ComplaintRegister.as_view(), name='complain_submit'),  # Submit new complaint
    path('fetch/', ComplaintRegister.as_view(), name='complain_details'),  # Keeping for backward compatibility
]