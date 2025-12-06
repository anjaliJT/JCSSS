from django.contrib import admin
# from .models import CSMApproval, CSMApprovalHistory, Team, QAQCReview
from .models import  *


# @admin.register(CSMApproval)
# class CSMApprovalAdmin(admin.ModelAdmin):
#     list_display = ("event", "status", "location", "remarks")
#     list_filter = ("status", "location")
#     search_fields = ("event__unique_token", "remarks")

admin.site.register(RepairLocation)
admin.site.register(RepairCost)

@admin.register(ComplaintStatus)
class ComplaintStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_unique_token",
        "status",
        "updated_at",
        "updated_by",
        "has_attachments",
    )
    
    search_fields = (
        "event__unique_token",      # from related Event model
        "status",                   # CharField with choices
    )
    list_filter = ("status", "updated_at", "updated_by")

    def event_unique_token(self, obj):
        return obj.event.unique_token
    event_unique_token.short_description = "Event Token"

    def has_attachments(self, obj):
        return "Yes" if obj.attachments else "No"
    has_attachments.short_description = "Attachment"

@admin.register(CustomerPricing)
class CustomerPricingAdmin(admin.ModelAdmin):
    list_display = ("id", "event_unique_token", "total_price", "approved", "created_at")
    search_fields = ("event__unique_token",)

    def event_unique_token(self, obj):
        return obj.event.unique_token
    event_unique_token.short_description = "Event Token"

