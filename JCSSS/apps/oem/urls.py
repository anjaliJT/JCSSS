"""
TO DO : 

plan of url patterns : 

urlpatterns = [
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'), Done
    path('complaint/<int:complaint_id>/update-status/', views.update_complaint_status, name='update_complaint_status'),
    path('complaint/<int:complaint_id>/add-cost/', views.add_repair_cost, name='add_repair_cost'),
    path('complaint/<int:complaint_id>/update-location/', views.update_repair_location, name='update_repair_location'),
    path('complaint/<int:complaint_id>/send-quote/', views.send_quote_to_customer, name='send_quote_to_customer'),
    path('complaint/<int:complaint_id>/approval/', views.customer_approval, name='customer_approval'),
]
"""

from django.urls import path
from apps.oem.views import *


urlpatterns = [
    # path("fetch/", ComplaintStatusView.as_view(), name="csm" ),
    path('complaint/<int:pk>/fetch/', ComplaintStatusView.as_view(), name='fetch_complaint_status'),
    
    path('complaint/<int:pk>/set-location/', set_complaint_location_view, name='set_complaint_location'),
    path('complaint/<int:pk>/update-location/', update_location_view, name='update_location'),


    # add, edit and delete Status
    path('complaint/<int:pk>/update-status/', UpdateStatusView.as_view(), name='update_complaint_status'),
    path('complaint/<int:pk>/edit-status/', edit_status_view, name='edit_status'),
    path('complaint/status/<int:status_id>/delete/', delete_status_view, name='delete_status'),

    # add and delete Cost
    path('complaint/<int:pk>/add-cost/', AddRepairCostView.as_view(), name='add_repair_cost'),
    path('repair-cost/<int:cost_id>/delete/', delete_repair_cost_view, name='delete_repair_cost'),

    path("complaints/<int:pk>/customer-cost/", CustomerCostView.as_view(), name="add_customer_cost"),

    
    # path("submit-report/<int:event_id>/", submit_report, name="submit_report"),
]

