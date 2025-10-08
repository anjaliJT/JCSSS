from django.contrib import admin
from .models import Product, Product_model  


# Register your models here.
@admin.register(Product_model)
class ProductModelAdmin(admin.ModelAdmin): 
    list_display = ("model_name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): 
    list_display  =  ("product_code","order_name","product_model","manufecturing_Date",
    "is_sold","sold_date","source_location","warranty_period","warranty_expiry_date")
    list_filter = ("product_model","is_sold")
    search_fields = ("product_code",)