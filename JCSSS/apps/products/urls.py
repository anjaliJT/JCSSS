from django.urls import  path
from .views import create_product, product_list,export_products,import_products

urlpatterns = [
    path("", product_list, name="product_list"),
    path("create/",create_product,name="create_product"),
    path("export/",export_products,name="export_products"),
    path("import/",import_products,name="import_products")
]