from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Event
from apps.oem.models import  ComplaintStatus
from apps.oem.tasks import send_mail_csm


# class ComplaintListView(LoginRequiredMixin, View):
#     login_url = 'login'
#     redirect_field_name = 'next'
    
#     template_name = "complaints/complaints_main_page.html"
    
#     def get(self, request):
#         # Get page number from request (default = 1)
#         page_number = request.GET.get('page', 1)

#         # Complaints
#         complaints = Event.objects.all().order_by('-date_of_occurrence')
#         status = request.GET.get('status')
#         uav = request.GET.get('uav')
#         search = request.GET.get('search')

#         if status:
#             complaints = complaints.filter(status=status)
#         if uav:
#             complaints = complaints.filter(tail_number=uav)

#         complaint_paginator = Paginator(complaints, 10)
#         complaints_page = complaint_paginator.get_page(page_number)

#         # Histories
#         histories = ComplaintStatus.objects.all().order_by("-id")
#         history_paginator = Paginator(histories, 10)
#         histories_page = history_paginator.get_page(page_number)

#         # Unique UAVs
#         uavs = Event.objects.values_list('uav_type', flat=True).distinct()

#         context = {
#             'complaints': complaints_page,
#             # 'approvals': approvals_page,
#             'histories': histories_page,
#             'uavs': uavs,
#             'current_filters': {
#                 'status': status,
#                 'uav': uav,
#                 'search': search,
#             },
#         }
        
#         return render(request, self.template_name, context)

from django.utils.dateparse import parse_date

class ComplaintListView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = "complaints/complaints_main_page.html"

    def get(self, request):
        page_number = request.GET.get('page', 1)
        status = request.GET.get('status') or ''
        uav = request.GET.get('uav') or ''
        search = request.GET.get('search') or ''

        # ✅ Fetch complaints
        complaints = Event.objects.all().order_by('-date_of_occurrence')

        if status:
            complaints = complaints.filter(
                complaint_statuses__status__iexact=status
            ).distinct()

        if uav:
            complaints = complaints.filter(uav_type__iexact=uav)

        if search:
            complaints = complaints.filter(model_number__icontains=search)

        # ✅ Paginate complaints only
        complaint_paginator = Paginator(complaints, 10)
        complaints_page = complaint_paginator.get_page(page_number)

        # ✅ Get unique UAV types for dropdown
        uavs = Event.objects.values_list('uav_type', flat=True).distinct()

        # ✅ Optional: Fetch last known complaint status per event
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
                send_mail_csm.delay(event.id)   # ✅ send to Celery worker
                return redirect("complaint_list") 

        except Exception as e:
            messages.error(request, f"Error submitting complaint: {str(e)}")
            print(str(e))
            # return render(request, self.template_name)
            return HttpResponse(f"Error : {e}") 

from django.shortcuts import get_object_or_404, render
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

