from django.contrib import admin
from apps.complain_form.models import *

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("unique_token",)
 
admin.site.register(Meteorology)   
admin.site.register(Attachment)   
admin.site.register(EventSeverityClassification)   
