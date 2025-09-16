from django.urls import path
from apps.oem.views import *
urlpatterns = [
    path("fetch/", CSMViews.as_view(), name="csm" )
]

