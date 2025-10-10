# apps/oem/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail

# from .models import Payment, RepairTask


# @receiver(post_save, sender=Payment)
# def handle_payment_approval(sender, instance, created, **kwargs):
#     # Only run if payment is approved
#     if instance.approved and instance.approved_at is None:
#         instance.approved_at = timezone.now()
#         instance.save(update_fields=["approved_at"])

#         # 1. Create RepairTask if not exists
#         if not instance.repair_task:
#             repair_task = RepairTask.objects.create(
#                 name=f"Repair for Payment {instance.id}",
#                 description="Auto-created when payment approved",
#                 status="pending"
#             )
#             instance.repair_task = repair_task
#             instance.save(update_fields=["repair_task"])

#         # 2. Start the task
#         instance.repair_task.start_task()

#         # 3. Send email notification
#         send_mail(
#             subject="Payment Approved - Repair Task Started",
#             message=f"Payment {instance.id} has been approved and repair task started (7 days).",
#             from_email="noreply@yourcompany.com",
#             recipient_list=["manager@yourcompany.com", "qa@yourcompany.com"],
#             fail_silently=False,
#         )
