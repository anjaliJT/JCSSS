from django.urls import  path
from .views import *

urlpatterns = [
    path("", product_list, name="product_list"),
    path("create/",create_product,name="create_product"),
    path("export/",export_products,name="export_products"),
    path("import/",import_products,name="import_products"),
    path('products/<int:pk>/edit/', edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', delete_product, name='delete_product'),
]