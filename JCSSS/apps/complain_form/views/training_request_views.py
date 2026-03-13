from ..models.complaint import UAVType
from ..models.spare_part_request import Items
from django.shortcuts import redirect, render 

def create_training_request(request): 
    print("entered here")
    uav_types = UAVType.objects.all() 
    items = Items.objects.all()
    # show form for spare part request


    return  render( request, "complaints/training-request/training_request_form.html",
                   {"uav_type":uav_types,
                    "items":items})