"""
TO DO : 

plan of url patterns : 

urlpatterns = [
    path('complaint/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<str:complaint_id>/update-status/', views.update_complaint_status, name='update_complaint_status'),
    path('complaint/<str:complaint_id>/add-cost/', views.add_repair_cost, name='add_repair_cost'),
    path('complaint/<str:complaint_id>/update-location/', views.update_repair_location, name='update_repair_location'),
    path('complaint/<str:complaint_id>/send-quote/', views.send_quote_to_customer, name='send_quote_to_customer'),
    path('complaint/<str:complaint_id>/approval/', views.customer_approval, name='customer_approval'),
]
"""

from django.urls import path
from apps.oem.views import *


urlpatterns = [
    # path("fetch/", CSMViews.as_view(), name="csm" ),
    # path("submit-report/<int:event_id>/", submit_report, name="submit_report"),
]

