from django.core.mail import send_mail
from django.conf import settings
# from apps.oem.models import  CSMApprovalHistory
from apps.users.models import CustomUser


# apps/oem/tasks.py
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Event, ComplaintStatus
from apps.users.models import CustomUser  # adjust import

@shared_task
def send_mail_csm(event_id):
    """
    Celery task to send complaint email and create approval records.
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return f"Event {event_id} not found"

    subject = f"[Complaint Registered] Event {event.unique_token}"
    message = (
        f"Dear CSM,\n\n"
        f"A new complaint has been registered.\n\n"
        f"Unique ID: {event.unique_token}\n"
        f"Pilot Name: {event.pilot_name}\n"
        f"Model Number: {event.model_number}\n"
        f"Date of Occurrence: {event.date_of_occurrence}\n"
        f"Description: {event.event_description}\n\n"
        f"Please review and take necessary actions.\n\n"
        f"Regards,\n"
        f"JTPL Customer System"
    )

    # ✅ Get all CSM emails
    recipient_list = list(
        CustomUser.objects.filter(role="CSM").values_list("email", flat=True)
    )

    if recipient_list:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

    # ✅ Create approval + history
    # csm_approval = CSMApproval.objects.create(event=event)

    ComplaintStatus.objects.create(
        event=event,
        status="REVIEW",
        remarks="Complaint registered, pending review",
    )

    return f"Mail sent for event {event.unique_token}"
