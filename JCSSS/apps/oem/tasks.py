# apps/oem/tasks.py
from celery import shared_task
from .models import Event
from .utils import send_mail_csm  # put your send_mail_csm function in utils.py

@shared_task
def send_mail_csm_task(event_id):
    try:
        event = Event.objects.get(id=event_id)
        send_mail_csm(event)  # your actual function
    except Event.DoesNotExist:
        pass
