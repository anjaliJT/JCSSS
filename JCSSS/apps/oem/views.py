from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from apps.complain_form.models import Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import date
from django.db.models import Sum
from apps.oem.forms import *
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.http import JsonResponse


class ComplaintStatusView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = ComplaintStatusForm()
        cost_form = RepairCostForm()

        statuses = event.complaint_statuses.order_by('updated_at')
        latest_status = statuses.last()
        status_choices = ComplaintStatus.STATUS_CHOICES
        location_choices = RepairLocation.LOCATION_CHOICES

        repair_cost = event.repair_costs.order_by('created_at')
        total_repair_cost = repair_cost.aggregate(total=Sum('repair_cost'))['total'] or 0

        customer_pricing = getattr(event, 'customer_pricing', None)
        total_customer_cost = customer_pricing.total_price if customer_pricing else 0

        # --- compute profit/loss ---
        trc = Decimal(str(total_repair_cost)) if total_repair_cost else Decimal('0')
        tcc = Decimal(str(total_customer_cost)) if total_customer_cost else Decimal('0')
        profit_value = tcc - trc
        profit_percent = None
        if trc != Decimal('0'):
            profit_percent = (profit_value / trc) * Decimal('100')
        # --- end compute ---
        
        # ✅ Always include location info — even if it doesn't exist yet
        location = getattr(event, 'location', None)
        location_data = {
            "id": location.id if location else "",
            "location": location.location if location else "",
            "remarks": location.remarks if location else "",
        }
        
        
        # --- Calculate total days based on statuses ---
        total_days = None
        today = timezone.now()
        review_status = statuses.filter(status="REVIEW").order_by('updated_at').first()
        accepted_status = statuses.filter(status="ACCEPTED").order_by('updated_at').first()
        closed_status = statuses.filter(status="CLOSED").order_by('updated_at').first()
        
        # CASE 1 – Closed exists → Calculate from ACCEPTED if possible
        if closed_status:
            if accepted_status:
                start_date = accepted_status.updated_at
            else:
                start_date = review_status.updated_at
                
            total_days = (closed_status.updated_at - start_date).days

        # CASE 2 – Not closed yet → Calculate till today
        else:
            if accepted_status:
                start_date = accepted_status.updated_at
                total_days = (today - start_date).days

            elif review_status:
                start_date = review_status.updated_at
                total_days = (today - start_date).days

            else:
                total_days = None  # nothing started yet

            

        return render(request, "complaints/complain_status.html", {
            "form": form,
            "cost_form": cost_form,
            "event": event,
            "statuses": statuses,
            "repair_cost": repair_cost,
            "total_repair_cost": total_repair_cost,
            "total_customer_cost": total_customer_cost,
            "latest_status": latest_status,
            "status_choices": status_choices,
            "location_data": location_data,# ✅ Always available in template
            "location_choices": location_choices,
            "profit_value": profit_value,
            "profit_percent": profit_percent,
            "total_days": total_days,
        })



@require_POST
def set_complaint_location_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    location_value = request.POST.get("location")
    remarks = request.POST.get("remarks", "")

    print("POST:", request.POST)
    print("Location value:", location_value)

    if location_value:
        RepairLocation.objects.create(
            event=event,
            location=location_value,
            remarks=remarks
        )

    return redirect("fetch_complaint_status", pk=pk)

@require_POST
def update_location_view(request, pk):
    location = get_object_or_404(RepairLocation, pk=pk)
    event = location.event
    print(location.location)

    if not location:
        return JsonResponse({"error": "No location found for this event."}, status=404)

    location_value = request.POST.get("location")
    remarks = request.POST.get("remarks")

    if not location_value:
        return JsonResponse({"error": "Location is required."}, status=400)

    location.location = location_value
    location.remarks = remarks
    location.save()
    
    print(location_value)
    messages.success(request, "Repair location updated.")
    return redirect("fetch_complaint_status", pk=event.id)
    


class UpdateStatusView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = ComplaintStatusForm(request.POST, request.FILES)
        if form.is_valid():
            status_instance = form.save(commit=False)
            status_instance.event = event
            status_instance.save()
            messages.success(request, "Complaint status updated successfully.")
            # ✅ Redirect to Status view
            return redirect("fetch_complaint_status", pk=pk)
        else:
            messages.error(request, "Error updating complaint status.")
        return redirect("fetch_complaint_status", pk=pk)


@require_POST
def edit_status_view(request, pk):
    status_obj = get_object_or_404(ComplaintStatus, pk=pk)

    status_obj.status = request.POST.get("status")
    status_obj.remarks = request.POST.get("remarks")

    if 'attachments' in request.FILES:
        status_obj.attachments = request.FILES['attachments']

    status_obj.save()

    return redirect("fetch_complaint_status", pk=status_obj.event.id)


@require_POST
def delete_status_view(request, status_id):
    status_obj = get_object_or_404(ComplaintStatus, id=status_id)
    event_id = status_obj.event.id  # Save event ID to redirect
    status_obj.delete()
    return redirect('fetch_complaint_status', pk=event_id)


class AddRepairCostView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = RepairCostForm(request.POST, request.FILES)
        if form.is_valid():
            repair = form.save(commit=False)
            repair.event = event
            repair.added_by = request.user
            repair.save()
            messages.success(request, "Repair cost added successfully.")
        else:
            messages.error(request, "Error adding repair cost.")
        # ✅ Redirect to Status view
        return redirect("fetch_complaint_status", pk=pk)


@require_POST
def delete_repair_cost_view(request, cost_id):
    cost_obj = get_object_or_404(RepairCost, id=cost_id)
    event_id = cost_obj.event.id
    cost_obj.delete()
    return redirect('fetch_complaint_status', pk=event_id)

class CustomerCostView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # Check if a record already exists
        try:
            pricing = event.customer_pricing
            form = CustomerPricingForm(request.POST, request.FILES, instance=pricing)
        except CustomerPricing.DoesNotExist:
            form = CustomerPricingForm(request.POST, request.FILES)

        if form.is_valid():
            customer_price = form.save(commit=False)
            customer_price.event = event
            customer_price.save()
            messages.success(request, "Customer pricing saved successfully.")
        else:
            messages.error(request, "Error saving customer pricing. Please check the form.")

        # Redirect to your main complaint status page (adjust name if needed)
        return redirect("fetch_complaint_status", pk=pk)


def customer_price_approve_view(request, pk):
    if request.method == "POST":
        pricing = get_object_or_404(CustomerPricing, pk=pk)
        pricing.approved = True
        pricing.save()
        messages.success(request, "You approved successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('fetch_complaint_status', pk=pk)






def attachemnts(instance, filename):
    # Store in a subfolder by event id (or date if you prefer)
    return f"complaints/{instance.event.id}/{filename}"