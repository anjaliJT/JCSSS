from django.shortcuts import render,redirect
from django.http import request, HttpResponse
from .models import Product, Product_model
from .Forms.product_form import productForm, uploadFileForm
import pandas as pd 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from datetime import datetime, date

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

        # Load data for the list view
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
            # Read CSV or Excel with proper handling of whitespace and quoted fields
            if file.name.endswith(".csv"): 
                df = pd.read_csv(
                    file,
                    dtype=str,  # Read all columns as strings initially
                    skipinitialspace=True,
                    on_bad_lines='warn'  # Don't fail on problematic lines
                )
            elif file.name.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file, dtype=str)
            else:
                messages.error(request, "Invalid file type. Please upload CSV or Excel.")
                return redirect("product_list")
            
            # Clean column names by removing any whitespace
            df.columns = df.columns.str.strip()

            # Check required columns
            required_columns = [
                "product_code", "order_name", "manufecturing_Date", 
                "is_sold", "sold_date", "source_location", "warranty_period", "army_command", "unit_name", "formation"
            ]
            
            # Convert column names to lowercase for case-insensitive comparison
            df_columns = [col.lower() for col in df.columns]
            required_columns_lower = [col.lower() for col in required_columns]
            
            missing = [col for col in required_columns if col.lower() not in df_columns]
            if missing:
                messages.error(
                    request, 
                    f"Missing required columns: {', '.join(missing)}. "
                    f"Download the correct template below."
                )
                return redirect("product_list")

            # Process rows
            for _, row in df.iterrows():
                try:
                    # Handle date formats with flexible parsing
                    manufecturing_date = pd.to_datetime(row["manufecturing_Date"]).date() if pd.notna(row["manufecturing_Date"]) else None
                    sold_date = pd.to_datetime(row["sold_date"]).date() if pd.notna(row["sold_date"]) else None
                    
                    # Handle boolean values more flexibly
                    is_sold = str(row.get("is_sold", "")).upper().strip() in ["TRUE", "YES", "1"]
                    
                    # Try to get product model from order_name
                    product_model = None
                    order_name = str(row.get("order_name", "")).strip()
                    if order_name:
                        product_model, _ = Product_model.objects.get_or_create(
                            model_name=order_name,
                            defaults={'model_name': order_name}
                        )
                    
                    # Handle warranty period conversion
                    warranty_str = str(row.get("warranty_period", "24 Months"))
                    warranty_period = 24  # default value
                    try:
                        # Extract the first number from the string
                        import re
                        numbers = re.findall(r'\d+', warranty_str)
                        if numbers:
                            warranty_period = int(numbers[0])
                    except ValueError:
                        pass  # Keep default value if conversion fails
                    
                    Product.objects.update_or_create(
                        product_code=str(row["product_code"]).strip(),
                        defaults={
                            "product_model": product_model,
                            "order_name": order_name,
                            "manufecturing_Date": manufecturing_date,
                            "is_sold": is_sold,
                            "sold_date": sold_date,
                            "source_location": str(row.get("source_location", "")).strip(),
                            "warranty_period": warranty_period,
                            "army_command": str(row.get("army_command", "")).strip(),
                            "unit_name": str(row.get("unit_name", "")).strip(),
                            "formation": str(row.get("formation", "")).strip(),
                        }
                    )
                except Exception as e:
                    messages.error(request, f"Error processing row {row['product_code']}: {str(e)}")
                    continue

            messages.success(request, "Products imported successfully.")
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




    



