from django.contrib import admin
from .models import Product, Product_model  


# Register your models here.
@admin.register(Product_model)
class ProductModelAdmin(admin.ModelAdmin): 
    list_display = ("model_name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): 
    list_display  =  ("tail_number","order_name","product_model","manufecturing_Date","warranty_period","warranty_expiry_date")
    list_filter = ("product_model",)
    search_fields = ("tail_number",)