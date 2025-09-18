from django.shortcuts import render,redirect
from django.http import request, HttpResponse
from .models import Product
from .Forms.product_form import productForm, uploadFileForm
import pandas as pd 
# Create your views here.

def create_product(request): 
    if request.method == "POST": 
        form  = productForm(request.POST)
        if form.is_valid() : 
            form.save() 
            return redirect("product_list")
    else:
        form = productForm()    
    
    return render(request,"products/product_form.html",{"form":form})
        
from django.contrib import messages
def product_list(request):
    messages.success(request, "Products loaded successfully!") 
    products = Product.objects.all() 
    return render(request, "products/products_main_page.html",{"products":products})

def import_products(request): 
    if request.method == "POST": 
        form = uploadFileForm(request.POST,request.FILES)
        if form.is_valid() : 
            file = request.FILES["file"]
            print("valid file", file)
            if file.name.endswith(".csv"): 
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            for _, row in df.iterrows() : 
                Product.objects.update_or_create(
                    product_code=row["product_code"],
                    defaults={
                        # "product_model":row["product_model"],
                        "order_name" : row["order_name"],
                        "manufecturing_Date":row["manufecturing_Date"],
                        "is_sold":row.get("is_sold",False),
                        "sold_date": row.get("sold_date"),
                        "source_location":row["source_location"],
                        "warranty_period":row.get("warranty_period",12),
                    }
                )
            print("product imported")
            return redirect("product_list")
        else:
        
            return HttpResponse("No file uploaded", status=400)

    return render(request, "products/product_form.html")
    
def export_products(request): 
    product_values = Product.objects.all().values()
    df = pd.DataFrame(product_values)
    response = HttpResponse(
        content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="products.xlsx"'
    df.to_excel(response,index=False)
    return response 


    



