from django.shortcuts import render,redirect
from django.http import request, HttpResponse
from .models import Product, Product_model
from .Forms.product_form import productForm, uploadFileForm
from datetime import date, timedelta
import pandas as pd 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import datetime

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
        

# views.py

# def product_list(request):
#     products = Product.objects.all()
#     models = Product_model.objects.all()
#     selected_model = request.GET.get("model")
#     print(selected_model)

#     if selected_model:
#         products = products.filter(product_model_id=selected_model)

#     return render(request, "products/products_main_page.html", {
#         "products": products,
#         "models": models,
#         "selected_model": selected_model,
#     })

def product_list(request):
    products = Product.objects.all()
    models = Product_model.objects.all()


    selected_model = request.GET.get("model")
    selected_status = request.GET.get("status")
    selected_warranty = request.GET.get("warranty")

    # Filter by product model
    if selected_model:
        products = products.filter(product_model_id=selected_model)

    # Filter by status
    if selected_status == "available":
        products = products.filter(is_sold=False)
    elif selected_status == "sold":
        products = products.filter(is_sold=True)

    # Warranty filtering
    today = date.today()
    if selected_warranty == "active":
        products = [p for p in products if p.warranty_expiry_date >= today]
    elif selected_warranty == "expired":
        products = [p for p in products if p.warranty_expiry_date < today]



    return render(request, "products/products_main_page.html", {
        "products": products,
        "models": models,
        "selected_model": selected_model,
        "selected_status": selected_status,
        "selected_warranty": selected_warranty,
    })
    

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Product_model

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        model_id = request.POST.get('product_model')
        if model_id:
            product.product_model = get_object_or_404(Product_model, pk=model_id)

        product.order_name = request.POST.get('order_name')

        manufacture_date_str = request.POST.get('manufecturing_Date')
        if manufacture_date_str:
            product.manufecturing_Date = datetime.strptime(manufacture_date_str, '%Y-%m-%d').date()

        product.save()

        # ✅ Load data for the list view
        products = Product.objects.all()
        models = Product_model.objects.all()

        return render(request, "products/products_main_page.html", {
            "products": products,
            "models": models,
            "selected_model": None,
            "selected_status": None,
            "selected_warranty": None,
        })
    print("edit.html")
    return render(request, 'edit_product.html', {
        'product': product,
        'product_models': Product_model.objects.all()
    })

@login_required(login_url='login')
def import_products(request): 
    if request.method == "POST": 
        if "import_file" not in request.FILES:
            messages.error(request, "⚠️ No file uploaded.")
            return redirect("product_list")

        file = request.FILES["import_file"]

        try:
            # Read CSV or Excel
            if file.name.endswith(".csv"): 
                df = pd.read_csv(file)
            elif file.name.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file)
            else:
                messages.error(request, "Invalid file type. Please upload CSV or Excel.")
                return redirect("product_list")

            # ✅ Check required columns
            required_columns = [
                "product_code", "order_name", "manufecturing_Date", 
                "is_sold", "sold_date", "source_location", "warranty_period"
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                messages.error(
                    request, 
                    f"Missing required columns: {', '.join(missing)}. "
                    f"Download the correct template below."
                )
                return redirect("product_list")

            # ✅ Process rows
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
            messages.success(request, "✅ Products imported successfully.")
            return redirect("product_list")

        except Exception as e:
            messages.error(request, f"Error while processing file: {str(e)}")
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




    



