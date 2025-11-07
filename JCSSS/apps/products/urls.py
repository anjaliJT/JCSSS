from django.urls import  path
from .views import *

urlpatterns = [
    path("", product_list_view, name="product_list"),
    path("create/",create_product_view,name="create_product"),
    path("export/",export_products_view,name="export_products"),
    path("import/",import_products_view,name="import_products"),
    path('<int:pk>/edit/', edit_product_view, name='edit_product'),
    path('<int:pk>/delete/', delete_product_view, name='delete_product'),
    path('<int:pk>/repair-history/', repair_history_view, name='repair_history'),
]