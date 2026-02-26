from celery import shared_task
import logging
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import mimetypes

from apps.oem.models import Event, ComplaintStatus
from apps.users.models import CustomUser
from django.db.transaction import on_commit

logger = logging.getLogger(__name__)


def _attach_file_to_email(email: EmailMessage, file_path=None, file_dict=None):
    try:
        if file_dict:
            name = file_dict.get("name")
            content = file_dict.get("content")
            mimetype = file_dict.get("mimetype") or mimetypes.guess_type(name)[0] or "application/octet-stream"
            email.attach(name, content, mimetype)

        elif file_path:
            with open(file_path, "rb") as f:
                content = f.read()
                name = file_path.split("/")[-1]
                mimetype = mimetypes.guess_type(name)[0] or "application/octet-stream"
                email.attach(name, content, mimetype)

    except Exception:
        logger.exception("Attachment failed")


@shared_task(bind=True, max_retries=3)
def send_notification_email_task(
    self,
    event_id,
    template_type,
    title,
    body,
    extra_context=None,
    attachment_paths=None,
):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        logger.warning("Event %s does not exist", event_id)
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

    if template_type == "customer_price":
        to_emails = [event.email] if event.email else []
        cc_emails = []
    else:
        to_emails = list(
            CustomUser.objects.filter(role="CSM").values_list("email", flat=True)
        )
        cc_emails = list(
            CustomUser.objects.exclude(role__in=["CUSTOMER", "CSM"])
            .values_list("email", flat=True)
        )

    if not to_emails:
        logger.info("No recipients found.")
        return

    subject = f"JASS {title}"

    html_body = render_to_string("emails/email_notification.html", context)

    email = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_emails,
        cc=cc_emails,
    )
    email.content_subtype = "html"

    if attachment_paths:
        for path in attachment_paths:
            _attach_file_to_email(email, file_path=path)

    try:
        email.send(fail_silently=False)
    except Exception as exc:
        logger.exception("Email failed, retrying...")
        raise self.retry(exc=exc, countdown=10)




def send_mail_async(event_id, template_type, title, body, extra_context=None, attachments=None):

    attachment_paths = []

    if attachments:
        if not isinstance(attachments, (list, tuple)):
            attachments = [attachments]

        for att in attachments:
            if hasattr(att, "path"):
                attachment_paths.append(att.path)

    on_commit(lambda: send_notification_email_task.delay(
        event_id,
        template_type,
        title,
        body,
        extra_context,
        attachment_paths
    ))