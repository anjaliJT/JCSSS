from django.views import View
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Event
from apps.oem.models import  ComplaintStatus
from apps.complain_form.utils import send_mail_thread
from django.db.models import Subquery, OuterRef

from django.db.models import Subquery, OuterRef, Q
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden


class ComplaintListView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = "complaints/complaints_main_page.html"

    def get(self, request):
        page_number = request.GET.get('page', 1)
        status = (request.GET.get('status') or '').strip()
        uav = (request.GET.get('uav') or '').strip()
        search = (request.GET.get('search') or '').strip()

        # Subquery to get latest status per event
        latest_status_subquery = ComplaintStatus.objects.filter(
            event=OuterRef('pk')
        ).order_by('-updated_at').values('status')[:1]

        # Base queryset annotated with latest_status
        complaints = Event.objects.annotate(
            latest_status=Subquery(latest_status_subquery)
        ).order_by('-date_of_occurrence')

        # Filter by status (latest status only)
        if status:
            complaints = complaints.filter(latest_status__iexact=status)

        # Filter by UAV type
        if uav:
            complaints = complaints.filter(uav_type__iexact=uav)

        # Multi-field search
        if search:
            # split words optionally (search terms), here we treat entire string as one term
            q = (
                Q(serial_number__icontains=search) |
                Q(pilot_name__icontains=search) |
                Q(tail_number__icontains=search) |
                Q(unique_token__icontains=search) |
                Q(organization__icontains=search) |
                Q(latest_status__icontains=search)
            )
            complaints = complaints.filter(q)

        # Paginate
        complaint_paginator = Paginator(complaints, 10)
        complaints_page = complaint_paginator.get_page(page_number)

        # UAV list for dropdown (distinct non-empty)
        uavs = Event.objects.exclude(uav_type="").values_list('uav_type', flat=True).distinct()

        # Optional: recent histories if you still need them
        histories = (
            ComplaintStatus.objects.select_related("event")
            .order_by("-updated_at")[:50]
        )

        context = {
            'complaints': complaints_page,
            'histories': histories,
            'uavs': uavs,
            'current_filters': {
                'status': status,
                'uav': uav,
                'search': search,
            },
        }
        return render(request, self.template_name, context)

class ComplaintRegister(LoginRequiredMixin,View):
    login_url = 'login'
    redirect_field_name = 'next'
    template_name = "complaints/complain_form.html"

    def get(self, request):
        return render(request, "complaints/complain_form.html")

    def post(self, request):
        try:
            with transaction.atomic():
                # Create Event
                event = Event.objects.create(
                    pilot_name=request.POST.get("pilot_name"),
                    certificate_number=request.POST.get("certificate_number"),
                    user = request.user,
                    filed_by=request.POST.get("filed_by"),   # Person who filed
                    designation=request.POST.get("designation"),
                    serial_number=request.POST.get("serial_number"),
                    date_of_occurrence=request.POST.get("date_of_occurrence"),
                    time_of_occurrence=request.POST.get("time_of_occurrence"),
                    field_site=request.POST.get("field_site"),
                    event_type=request.POST.get("event_type"),
                    damage_level=request.POST.get("damage_level"),
                    flight_mode=request.POST.get("flight_mode"),
                    event_phase=request.POST.get("event_phase"),
                    uav_type=request.POST.get("uav_type"),
                    tail_number=request.POST.get("tail_number"),
                    gcs_type=request.POST.get("gcs_type"),
                    gcs_number=request.POST.get("gcs_number"),
                    uav_weight=request.POST.get("uav_weight"),
                    event_description=request.POST.get("event_description"),
                    initial_actions_taken=request.POST.get("initial_actions_taken"),
                    remarks=request.POST.get("remarks"),
                    organization=request.POST.get("organization"),
                # )

                # # 2️⃣ Create Meteorology
                # Meteorology.objects.create(
                #     event=event,
                    wind=request.POST.get("wind"),
                    temperature=request.POST.get("temperature"),
                    pressure_qnh=request.POST.get("pressure_qnh"),
                    # visibility=request.POST.get("visibility"),
                    # clouds=request.POST.get("clouds"),
                    # humidity=request.POST.get("humidity"),
                    turbulence=bool(request.POST.get("turbulence")),
                    windshear=bool(request.POST.get("windshear")),
                    rain=bool(request.POST.get("rain")),
                    icing=bool(request.POST.get("icing")),
                    snow=bool(request.POST.get("snow")),
                # )

                # # 3️⃣ Create Attachments
                # Attachment.objects.create(
                #     event=event,
                    file_video=request.FILES.get("video"),
                    file_image1=request.FILES.get("photo1"),
                    file_image2=request.FILES.get("photo2"),
                    file_image3=request.FILES.get("photo3"),
                    file_log=request.FILES.get("log_file"),
                    
                #     )
                
                # # 4️⃣ create EventSeverityClassification
                # EventSeverityClassification.objects.create(
                #     event=event,
                    damage_potential = request.POST.get("damage_level"),
                )

                messages.success(request, "Complaint submitted successfully!")

                template_type = "complaint"  # choose appropriate type for this endpoint
                title = f"New complaint {event.unique_token}"
                body = f"A new complaint request comes. Please review it and take necessary actions."

                # launch email send in background
                send_mail_thread(event.id, template_type=template_type, title=title, body=body, extra_context={"complaint":event
                })
                ComplaintStatus.objects.create(
                    event= event,
                )
                return redirect("complaint_list") 

        except Exception as e:
            messages.error(request, f"Error submitting complaint: {str(e)}")
            print(str(e))
            # return render(request, self.template_name)
            return HttpResponse(f"Error : {e}") 

class ComplaintDetailView(LoginRequiredMixin,View):
    template_name = "complaints/complain_form.html"

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        messages.info(request,"You only view your details.")

        is_completed = bool(event)

        return render(
            request,
            self.template_name,
            {
                "event": event,
                "is_readonly": True,
                "is_completed": is_completed,
            },
        )

    # views.py


class ComplaintEditView(LoginRequiredMixin,View):
    template_name = "complaints/complain_form.html"

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        messages.info(request,"You only view your details.")

        is_completed = bool(event)

        return render(
            request,
            self.template_name,
            {
                "event": event,
                "is_readonly": False,
                "is_valid": True,
                "is_completed": is_completed,
            },
        )


    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # permission check
        if not (request.user == event.user or request.user.is_staff):
            return HttpResponseForbidden("You don't have permission to edit this complaint.")

        try:
            with transaction.atomic():
                # ---------- Basic fields ----------
                event.pilot_name = request.POST.get("pilot_name", event.pilot_name)
                event.email = request.POST.get("email", event.email)
                event.certificate_number = request.POST.get("certificate_number", event.certificate_number)
                event.filed_by = request.POST.get("filed_by", event.filed_by)
                event.designation = request.POST.get("designation", event.designation)
                event.serial_number = request.POST.get("serial_number", event.serial_number)
                event.field_site = request.POST.get("field_site", event.field_site)
                event.event_type = request.POST.get("event_type", event.event_type)
                event.damage_level = request.POST.get("damage_level", event.damage_level)
                event.flight_mode = request.POST.get("flight_mode", event.flight_mode)
                event.event_phase = request.POST.get("event_phase", event.event_phase)
                event.event_description = request.POST.get("event_description", event.event_description)
                event.initial_actions_taken = request.POST.get("initial_actions_taken", event.initial_actions_taken)
                event.remarks = request.POST.get("remarks", event.remarks)
                event.organization = request.POST.get("organization", event.organization)
                event.tail_number = request.POST.get("tail_number", event.tail_number)
                event.uav_type = request.POST.get("uav_type", event.uav_type)
                event.gcs_type = request.POST.get("gcs_type", event.gcs_type)
                event.gcs_number = request.POST.get("gcs_number", event.gcs_number)

                # ---------- Date/time fields ----------
                date_val = request.POST.get("date_of_occurrence")
                time_val = request.POST.get("time_of_occurrence")
                if date_val:
                    event.date_of_occurrence = date_val
                # keep previous if not provided; similarly for time
                if time_val:
                    event.time_of_occurrence = time_val

                # ---------- Numeric fields ----------
                uav_weight = request.POST.get("uav_weight")
                if uav_weight:
                    try:
                        event.uav_weight = float(uav_weight)
                    except ValueError:
                        # ignore and keep old value (or set to 0.0 if you prefer)
                        pass

                # ---------- Meteorology booleans (checkboxes) ----------
                # Checkbox presence in POST means checked
                event.turbulence = "turbulence" in request.POST
                event.windshear = "windshear" in request.POST
                event.rain = "rain" in request.POST
                event.icing = "icing" in request.POST
                event.snow = "snow" in request.POST

                # ---------- Files: replace only if new file uploaded ----------
                # For each file field, set only when a new file exists in request.FILES
                if request.FILES.get("video"):
                    event.file_video = request.FILES.get("video")
                if request.FILES.get("photo1"):
                    event.file_image1 = request.FILES.get("photo1")
                if request.FILES.get("photo2"):
                    event.file_image2 = request.FILES.get("photo2")
                if request.FILES.get("photo3"):
                    event.file_image3 = request.FILES.get("photo3")
                if request.FILES.get("log_file"):
                    event.file_log = request.FILES.get("log_file")

                # ---------- Severity/damage pote ntial ----------
                # You have both damage_level (string) and damage_potential (choice). Map as you like:
                dp = request.POST.get("damage_level")
                if dp:
                    # if damage_potential is stored in damage_potential field:
                    event.damage_potential = dp.capitalize() if dp else event.damage_potential

                # Save the event
                event.save()

                messages.success(request, "Complaint updated successfully.")
                return redirect("complaint_list")

        except Exception as e:
            # Log / flash error
            messages.error(request, f"Error updating complaint: {str(e)}")
            print("ComplaintEdit error:", str(e))
            # Re-render with existing event data and error message
            return render(request, self.template_name, {
                "event": event,
                "is_readonly": False,
            })

