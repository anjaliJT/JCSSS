# from django.shortcuts import render
# from django.views import View
# # Create your views here.

# class ComplaintRegister(View):
#     def get(self, request):
#         return render(request, "users/complain_form.html")
    
from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.db import transaction

from .models import Event, Meteorology, Attachment, EventSeverityClassification

from apps.oem.tasks import send_mail_csm


class ComplaintRegister(View):
    template_name = "complaints/complain_form.html"

    def get(self, request):
        return render(request, "complaints/complaints_main_page.html")

    def post(self, request):
        try:
            with transaction.atomic():
                # 1️⃣ Create Event
                event = Event.objects.create(
                    pilot_name=request.POST.get("pilot_name"),
                    certificate_number=request.POST.get("certificate_number"),
                    user = request.user,
                    filed_by=request.POST.get("filed_by"),   # Person who filed
                    designation=request.POST.get("designation"),
                    model_number=request.POST.get("model_number"),
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
                )

                # 2️⃣ Create Meteorology
                Meteorology.objects.create(
                    event=event,
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
                )

                # 3️⃣ Create Attachments
                Attachment.objects.create(
                    event=event,
                    file_video=request.FILES.get("video"),
                    file_image1=request.FILES.get("photo1"),
                    file_image2=request.FILES.get("photo2"),
                    file_image3=request.FILES.get("photo3"),
                    file_log=request.FILES.get("log_file"),
                    )
                
                # 4️⃣ create EventSeverityClassification
                EventSeverityClassification.objects.create(
                    event=event,
                    damage_potential = request.POST.get("damage_level"),
                )

                messages.success(request, "Complaint submitted successfully!")
                send_mail_csm.delay(event.id)   # ✅ send to Celery worker
                # return redirect("complain_form")  # replace with your success URL
                return HttpResponse("Submitted")  # replace with your success URL

        except Exception as e:
            messages.error(request, f"Error submitting complaint: {str(e)}")
            print(str(e))
            # return render(request, self.template_name)
            return HttpResponse("Error") 


class UserDetails_dummy(View):
    def get(self, request):
        return render(request, "complaints/complaints_main_page.html")