from django.contrib import admin
# from .models import CSMApproval, CSMApprovalHistory, Team, QAQCReview
from .models import CSMApproval, CSMApprovalHistory, ReviewReport


# @admin.register(CSMApproval)
# class CSMApprovalAdmin(admin.ModelAdmin):
#     list_display = ("event", "status", "location", "remarks")
#     list_filter = ("status", "location")
#     search_fields = ("event__unique_token", "remarks")

admin.site.register(CSMApproval)
admin.site.register(CSMApprovalHistory)
# admin.site.register(Team)
admin.site.register(ReviewReport)
