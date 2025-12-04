from django.urls import path
from apps.complain_form.views import ComplaintRegister, ComplaintListView, ComplaintDetailView,ComplaintEditView

# app_name = "complaints"

urlpatterns = [
    path('submit/', ComplaintRegister.as_view(), name='complain_submit'),  # Submit new complaint
    path('fetch/', ComplaintRegister.as_view(), name='complain_detail'),  # Keeping for backward compatibility
    path("complain/list/", ComplaintListView.as_view(), name="complaint_list"),
    # path("complaint/<int:pk>/edit/", ComplaintEdit.as_view(), name="complaint_edit"),  # Option 1
    path("complain/<int:pk>/detail/", ComplaintDetailView.as_view(), name="complaint_detail"),
    path("complain/<int:pk>/edit/", ComplaintEditView.as_view(),name="complaint_edit")
]