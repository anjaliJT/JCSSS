from django.urls import  path
from .views import create_product, product_list,export_products,import_products

urlpatterns = [
    path("products/create",create_product,name="create_product"),
    path("products", product_list, name="product_list"),
    path("products/export",export_products,name="export_products"),
    path("products/import",import_products,name="import_products")
]