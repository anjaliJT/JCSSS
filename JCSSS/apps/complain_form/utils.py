# utils/email_thread.py
import threading
import logging

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import mimetypes
from django.core.files.base import File

from django.db.models import Q

from apps.oem.models import Event, ComplaintStatus
from apps.users.models import CustomUser

logger = logging.getLogger(__name__)

def _attach_file_to_email(email: EmailMessage, file_field):
    """
    Attach a Django FileField (or file-like) to an EmailMessage.
    file_field can be:
      - a Django FileField instance (e.g. customer_pricing.invoice)
      - a dict: {"name": "...", "content": b"...", "mimetype": "application/pdf"}
    """
    try:
        if not file_field:
            return

        # Case: dict with explicit name/content
        if isinstance(file_field, dict):
            name = file_field.get("name")
            content = file_field.get("content")
            mimetype = file_field.get("mimetype") or mimetypes.guess_type(name)[0] or "application/octet-stream"
            if name and content:
                email.attach(name, content, mimetype)
            return

        # Assume file_field is a Django FileField or File (file_field.field/file_field.file)
        # Use the storage to open/read safely
        # If the FileField is a model field (e.g. instance.invoice), use file_field.path or file_field.open()
        if hasattr(file_field, "open"):
            file_field.open(mode="rb")
            content = file_field.read()
            name = getattr(file_field, "name", None) or getattr(file_field, "filename", "attachment")
            mimetype = mimetypes.guess_type(name)[0] or "application/octet-stream"
            email.attach(name.split("/")[-1], content, mimetype)
            try:
                file_field.close()
            except Exception:
                pass
            return

        logger.debug("Unknown attachment type; skipping attachment: %r", type(file_field))
    except Exception:
        logger.exception("Failed attaching file to email")
        
        
def _send_email_sync(event_id, template_type, title, body, extra_context=None, attachments=None, value=None):
    """
    Synchronous function that builds and sends the email.
    Can be run inside a background thread. Supports attaching invoice files.
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        logger.warning("Event %s does not exist, skipping email.", event_id)
        return

    latest_status_obj = ComplaintStatus.objects.filter(event=event).order_by("-updated_at").first()
    latest_status = latest_status_obj.status if latest_status_obj else "REVIEW"

    context = {
        "user": "Support Team",
        "title": title,
        "body": body,
        "event": event,
        "latest_status": latest_status,
        "template_type": template_type,
    }
    if extra_context:
        context.update(extra_context)
        
    # ✅ Add this block:
    if attachments:
        context["attachments"] = attachments
        
    # To: All CSM role users
    if template_type == "customer_price":
        
        # CC: Everyone except CUSTOMER and except CSM
        cc_qs = CustomUser.objects.filter(role__in=["DIRECTOR"])
        cc_emails = list(cc_qs.values_list("email", flat=True))
    else:
        # CC: Everyone except CUSTOMER and except CSM
        cc_qs = CustomUser.objects.exclude(role__in=["CUSTOMER", "CSM"])
        cc_emails = list(cc_qs.values_list("email", flat=True))
    
    to_emails = list(
            CustomUser.objects.filter(role="CSM").values_list("email", flat=True)
        )
    
    
    if not to_emails:
        logger.info("No CSM recipients found for event %s. Skipping email.", event_id)
        return

    
    subject = f"JCSSS {title}"

    try:
        html_body = render_to_string("emails/email_notification.html", context)
        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
            cc=cc_emails,
        )
        email.content_subtype = "html"

        # Attach files if provided
        if attachments:
            # attachments can be a list or a single item
            if not isinstance(attachments, (list, tuple)):
                attachments = [attachments]
            for att in attachments:
                _attach_file_to_email(email, att)

        email.send(fail_silently=False)
        logger.info("Notification email sent for event %s to %s", event_id, to_emails)
    except Exception:
        logger.exception("Failed to send notification email for event %s", event_id)


def _send_customer_price_email(event_id, title, body, extra_context=None, attachments=None):
    # Only customer-specific email
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return

    to_email = event.email
    print(event.email)
    print(event.pilot_name)
    if not to_email:
        return

    context = {
        "user": event.pilot_name,
        "title": title,
        "body": body,
        "event": event,
        "template_type": "customer_price",
    }
    if extra_context:
        context.update(extra_context)

    subject = f"JCSSS {title}"

    html_body = render_to_string("emails/email_notification.html", context)

    email = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        cc=[],  # No CC for customer
    )
    email.content_subtype = "html"

    if attachments:
        if not isinstance(attachments, (list, tuple)):
            attachments = [attachments]
        for att in attachments:
            _attach_file_to_email(email, att)

    email.send(fail_silently=False)


def send_mail_thread(event_id, template_type, title, body, extra_context=None, attachments=None, value=None):

    if template_type == "customer_price":
        # 1st email → customer only
        thread_1 = threading.Thread(
            target=_send_customer_price_email,
            args=(event_id, title, body),
            kwargs={"extra_context": extra_context, "attachments": attachments},
            daemon=True,
        )
        thread_1.start()
        # print("start thread1----------------")

        # 2nd email → internal team
        thread_2 = threading.Thread(
            target=_send_email_sync,
            args=(event_id, template_type, title, body),
            kwargs={"extra_context": extra_context, "attachments": attachments, "value": value},
            daemon=True,
        )
        thread_2.start()
        # print("start thread2---------------")

        return thread_1, thread_2

    else:
        # normal
        thread = threading.Thread(
            target=_send_email_sync,
            args=(event_id, template_type, title, body),
            kwargs={"extra_context": extra_context, "attachments": attachments, "value": value},
            daemon=True,
        )
        thread.start()
        # print("start------------------")
        return thread
