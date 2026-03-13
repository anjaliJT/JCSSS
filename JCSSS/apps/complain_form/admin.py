from django.contrib import admin
from apps.complain_form.models import *

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("unique_token",)
 
admin.site.register(UAVType)   
admin.site.register(Items)   
admin.site.register(SparePartsRequest)
admin.site.register(SparePartRequestItems)
admin.site.register(TrainingRequest)


# admin.site.register(EventSeverityClassification)   
