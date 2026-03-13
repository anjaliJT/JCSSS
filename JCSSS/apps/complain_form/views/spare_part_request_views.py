from ..models.complaint import UAVType
from ..models.spare_part_request import Items, SparePartRequestItems, SparePartsRequest
from django.shortcuts import redirect, render 
from django.db import transaction

def create_spare_request(request): 
    print("entered here")
    uav_types = UAVType.objects.all() 
    items = Items.objects.all()
    if request.method=="POST": 
        data = {
        "request_by" : request.POST.get("request_by"),
        "unit_name" : request.POST.get("command_name"),
        "service_request_id" : request.POST.get("service_request_id"),
        "uav_type_id" : request.POST.get("uav_type"),
        "tail_number" : request.POST.get("tail_number"),
        "remarks" :request.POST.get("remarks"),
        "created_at" : request.POST.get("created_at"),
        }

        with transaction.atomic(): 
            spare_request = SparePartsRequest.objects.create(**data) 
    
        request_items = []
        for key,value in request.POST.items():
            pass 

    # show form for spare part request
    return  render( request, "complaints/spare-parts/spare_parts_request_form.html",
                   {"uav_types":uav_types,
                    "items":items})

# def create_items_view(request): 
#     if request.method=="POST":
#         data = {
#         "uav_type_id" : request.POST.get("uav_type"),
#         "item_name" : request.POST.get("items_name"),
#         }

#         Items.objects.create(**data)

    # return alert message

def spare_request_details(): 
    pass 

def update_spare_request(request,id): 
    pass 

def submit_request_view():
    # save request 
    pass

def get_parts(request):
    # return parts of selected UAV /Products
    pass

def update_availability_status(request): 
    pass

def mark_approval(): 
    pass

def mark_dispatch_status(): 
    pass 

def update_cost():
    pass


