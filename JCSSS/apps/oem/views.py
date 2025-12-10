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
from apps.complain_form.utils import send_mail_thread



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

        # Always include location info
        location = getattr(event, 'location', None)
        location_data = {
            "id": location.id if location else "",
            "location": location.location if location else "",
            "remarks": location.remarks if location else "",
        }

        # --- timing logic ---
        total_days = None       # days from PRODUCT_RECEIVED to CLOSED (if closed) or to today (if not)
        timing_status = "Not Started"   # One of: "Not Started", "On Time", "Late"
        timing_stage = None     # helpful string: "awaiting_diagnosis", "awaiting_repair", "closed", etc.

        today = timezone.now()

        received_status  = statuses.filter(status="PRODUCT_RECEIVED").order_by('updated_at').first()
        diagnosis_status = statuses.filter(status="DIAGNOSIS").order_by('updated_at').first()
        repair_status    = statuses.filter(status="REPAIR").order_by('updated_at').first()
        closed_status    = statuses.filter(status="CLOSED").order_by('updated_at').first()

        if not received_status:
            # No product received yet → process not started
            total_days = None
            timing_status = "Not Started"
            timing_stage = "not_started"

        else:
            start_date = received_status.updated_at
            end_date = closed_status.updated_at if closed_status else today
            total_days = (end_date - start_date).days

            pricing = getattr(event, 'customer_pricing', None)
            approved = pricing.approved if pricing else False

            # ✅ If already closed: final rule wins (10-day total window from PRODUCT_RECEIVED)
            if closed_status:
                timing_stage = "closed"
                timing_status = "On Time" if total_days <= 10 else "Late"

            else:
                # 🚩 Not closed yet — apply phase-based rules

                # 1️⃣ PRODUCT_RECEIVED + DIAGNOSIS must be completed within 3 days
                if not diagnosis_status:
                    # Still waiting for DIAGNOSIS
                    timing_stage = "awaiting_diagnosis"
                    days_since_received = (today - start_date).days
                    timing_status = "Late" if days_since_received > 3 else "On Time"

                # DIAGNOSIS done but payment not yet approved
                elif not approved:
                    timing_stage = "awaiting_payment_approval"
                    days_since_received = (today - start_date).days
                    # Still same 3-day SLA for received+diagnosis+approval side
                    timing_status = "Late" if days_since_received > 3 else "On Time"

                else:
                    # 2️⃣ Payment approved – now we look at REPAIR window

                    if not repair_status:
                        # Payment approved but repair not started yet
                        timing_stage = "awaiting_repair"
                        # No explicit SLA given here; keep an overall 10-day guard from PRODUCT_RECEIVED
                        days_since_received = (today - start_date).days
                        timing_status = "Late" if days_since_received > 10 else "On Time"
                    else:
                        # Repair started – 7 days allowed from REPAIR to (future) CLOSED
                        timing_stage = "under_repair"
                        days_since_repair = (today - repair_status.updated_at).days
                        timing_status = "Late" if days_since_repair > 7 else "On Time"
        # --- end timing logic ---


        # pass timing_status & timing_stage to template so template can show accurate badge/text
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
            "location_data": location_data,
            "location_choices": location_choices,
            "profit_value": profit_value,
            "profit_percent": profit_percent,
            "total_days": total_days,
            "timing_status": timing_status,
            "timing_stage": timing_stage,
        })


@require_POST
def set_complaint_location_view(request, pk):
    """
    Save a RepairLocation (if provided) and trigger a notification email in a background thread.
    """
    event = get_object_or_404(Event, pk=pk)
    location_value = request.POST.get("location")
    remarks = request.POST.get("remarks", "").strip()

    if location_value:
        RepairLocation.objects.create(
            event=event,
            location=location_value,
            remarks=remarks
        )
        messages.success(request, "Location saved successfully.")
    else:
        messages.warning(request, "No location provided.")

    # Compose email content and choose template_type
    template_type = "location"  # choose appropriate type for this endpoint
    title = f"Location Set for complaint {event.unique_token}"
    body = f"Repair location mode is set to: {location_value or 'N/A'}."

    # launch email send in background
    send_mail_thread(event.id, template_type=template_type, title=title, body=body, extra_context={
        "location": location_value,
        "remarks": remarks,
        "updated_by":request.user.first_name
    })

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
    
    # print(location_value)
    messages.success(request, "Repair location updated.")
    template_type = "location"  # choose appropriate type for this endpoint
    title = f"Location Updated for complaint {event.unique_token}"
    body = f"Repair location mode is now changed to: {location_value or 'N/A'}\nRemarks: {remarks}"

    # launch email send in background
    send_mail_thread(event.id, template_type=template_type, title=title, body=body, extra_context={
        "location": location_value,
        "remarks": remarks,
    })
    
    return redirect("fetch_complaint_status", pk=event.id)
    

class UpdateStatusView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = ComplaintStatusForm(request.POST, request.FILES)
        if form.is_valid():
            status_instance = form.save(commit=False)
            status_instance.event = event
            status_instance.updated_by = request.user   # ✅ FIX
            status_instance.save()
            messages.success(request, "Complaint status updated successfully.")
            # ✅ Redirect to Status view
            
            template_type = "status"  # choose appropriate type for this endpoint
            title = f"Status Updated for complaint {event.unique_token}"
            body = f"Model number {event.serial_number} status has been updated to { status_instance.status }."
            attachments = None
            if status_instance.attachments:
                attachments = status_instance.attachments
                
            # diagnosis_by = None
            # if status_instance.status == "DIAGNOSIS":
            #     diagnosis_by = status_instance.updated_by.first_name

            # launch email send in background
            send_mail_thread(event.id, template_type=template_type, title=title, 
            body=body, 
            attachments=attachments,
            extra_context={
                "Current Status": status_instance.status,
                "remarks": status_instance.remarks,
                # "diagnosis_by":diagnosis_by,
                "updated_by":request.user.first_name,
            }
            )
    
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
            
            # --- Correct total calculation for this event ---
            agg = RepairCost.objects.filter(event=event).aggregate(total=Sum("repair_cost"))
            total = agg.get("total") or 0

            # Format numbers (two decimals). Use commas for thousands.
            new_cost_str = f"₹{repair.repair_cost:,.2f}"
            total_str = f"₹{total:,.2f}"

            template_type = "approval"
            title = f"Repair Cost Added {event.unique_token}"
            body = f"New repair cost is added: {new_cost_str}. Total repair cost for this product is {total_str}."

            # Attach invoice file if present — pass FileField (your helper expects this)
            attachments = None
            if getattr(repair, "attachment", None):
                attachments = repair.attachment

            # Launch email sending in background thread
            send_mail_thread(
                event_id=event.pk,
                template_type=template_type,
                title=title,
                body=body,
                extra_context=None,
                attachments=attachments,
            )
            
            
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
            
            template_type = "customer_price"
            title = f"Invoice for Complaint {event.unique_token}"
            body = f"Total cost in repairing is: ₹{customer_price.total_price}"

            # price_details to render inside template
            price_details = f"Total: ₹{customer_price.total_price}"

            # Attach invoice file if present
            attachments = None
            if customer_price.invoice:
                # pass the FileField itself — helper will open/read it
                attachments = customer_price.invoice

            # Launch email sending in background thread
            send_mail_thread(
                event_id=pk,
                template_type=template_type,
                title=title,
                body=body,
                extra_context={"price_details": price_details},
                attachments=attachments,
            )
            
        else:
            messages.error(request, "Error saving customer pricing. Please check the form.")

        # Redirect to your main complaint status page (adjust name if needed)
        return redirect("fetch_complaint_status", pk=pk)


def customer_price_approve_view(request, pk):
    if request.method == "POST":
        pricing = get_object_or_404(CustomerPricing, pk=pk)
        pricing.approved = True
        pricing.approved_at = timezone.now()
        pricing.save()
        messages.success(request, "You approved successfully.")
        
        template_type = "approval"
        title = f"Repair Cost Approved {pricing.event.unique_token}"
        body = f"Repair cost is approved by customer of {pricing.total_price}rs."


        # Launch email sending in background thread
        send_mail_thread(
                event_id = pricing.event.id,
                template_type=template_type,
                title=title,
                body=body,
                extra_context=None,
            )
            
            
    else:
        messages.error(request, "Invalid request method.")
    return redirect('fetch_complaint_status', pk=pk)



def attachemnts(instance, filename):
    # Store in a subfolder by event id (or date if you prefer)
    return f"complaints/{instance.event.id}/{filename}"