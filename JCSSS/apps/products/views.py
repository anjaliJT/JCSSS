from django.shortcuts import render,redirect
from django.http import request, HttpResponse
from .models import Product
from .Forms.product_form import productForm, uploadFileForm
import pandas as pd 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
@login_required(login_url = 'login')
def create_product(request): 
    if request.method == "POST": 
        form  = productForm(request.POST)
        if form.is_valid() : 
            form.save() 
            return redirect("product_list")
    else:
        form = productForm()    
    
    return render(request,"products/product_form.html",{"form":form})
        

@login_required(login_url='login')
def product_list(request):
    messages.success(request, "Products loaded successfully!") 
    products = Product.objects.all() 
    return render(request, "products/products_main_page.html",{"products":products})




@login_required(login_url='login')
def import_products(request): 
    if request.method == "POST": 
        if "import_file" not in request.FILES:
            return HttpResponse("No file uploaded", status=400)

        file = request.FILES["import_file"]
        print("valid file:", file.name)

        # Read CSV or Excel
        if file.name.endswith(".csv"): 
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Loop through rows and update/create products
        for _, row in df.iterrows():
            Product.objects.update_or_create(
                product_code=row["product_code"],
                defaults={
                    "order_name": row.get("order_name"),
                    "manufecturing_Date": row.get("manufecturing_Date"),
                    "is_sold": row.get("is_sold", False),
                    "sold_date": row.get("sold_date"),
                    "source_location": row.get("source_location"),
                    "warranty_period": row.get("warranty_period", 12),
                }
            )
        print("product imported")
        return redirect("product_list")

    return render(request, "products/product_form.html")


   

@login_required(login_url='login')
def export_products(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    products = Product.objects.all()

    if from_date and to_date:
        products = products.filter(manufecturing_Date__range=[from_date, to_date])

    df = pd.DataFrame(products.values())

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="products.xlsx"'
    df.to_excel(response, index=False)
    return response




    



