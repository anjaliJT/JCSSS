from django.urls import path, include

urlpatterns = [
    path('', include('apps.users.urls')),
    path('complain/', include('apps.complain_form.urls')),
    path('product/',include('apps.products.urls')),
    path('csm/', include('apps.oem.urls')),
]