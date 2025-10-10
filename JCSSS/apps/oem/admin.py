from django.contrib import admin
# from .models import CSMApproval, CSMApprovalHistory, Team, QAQCReview
from .models import  *


# @admin.register(CSMApproval)
# class CSMApprovalAdmin(admin.ModelAdmin):
#     list_display = ("event", "status", "location", "remarks")
#     list_filter = ("status", "location")
#     search_fields = ("event__unique_token", "remarks")

admin.site.register(Location)
admin.site.register(ComplaintStatus)
admin.site.register(RepairCost)
admin.site.register(CustomerPricing)
# admin.site.register(Payment)
