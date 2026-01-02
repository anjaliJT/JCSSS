from datetime import timedelta
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Exists
from apps.complain_form.models import Event
from apps.oem.models import ComplaintStatus


def compute_active_complain(user):

    # Latest status
    latest_status = ComplaintStatus.objects.filter(
        event=OuterRef("pk")
    ).order_by("-updated_at").values("status")[:1]

    # Latest status update time
    latest_status_updated_on = ComplaintStatus.objects.filter(
        event=OuterRef("pk")
    ).order_by("-updated_at").values("updated_at")[:1]

    # ✅ Check if event EVER had REPAIR
    has_repair_status = ComplaintStatus.objects.filter(
        event=OuterRef("pk"),
        status="REPAIR"
    )

    # Filter by role
    if user.role == "CUSTOMER":
        events = Event.objects.filter(user=user)
    else:
        events = Event.objects.all()

    # Annotate
    events = events.annotate(
        latest_status=Subquery(latest_status),
        latest_status_updated_on=Subquery(latest_status_updated_on),
        had_repair_status=Exists(has_repair_status),
    ).order_by("-id")

    # Date logic
    today = timezone.now()
    week_start = today - timedelta(days=7)

    # Progress mapping (✅ fixed keys)
    progress_map = {
        "IN REVIEW": 10,
        "ACCEPTED": 25,
        "PRODUCT RECEIVED": 35,
        "DIAGNOSIS REPORT": 40,
        "REPAIR": 55,
        "CTF": 75,
        "READY FOR DISPATCH": 85,
        "CLOSED": 100,
    }

    # Latest 4 events
    event_data = []
    for e in events[:4]:
        event_data.append({
            "serial_number": e.serial_number,
            "tail_number": e.tail_number,
            "current_status": e.latest_status,
            "progress": progress_map.get(e.latest_status, 25),
        })

    return {
        # Counts
        "total_count": events.count(),

        "open_status_count": events.exclude(
            latest_status="CLOSED"
        ).count(),

        # ✅ FIXED
        "pending_status_count": events.filter(
            latest_status="IN REVIEW"
        ).count(),

        "resolved_this_week_count": events.filter(
            latest_status="CLOSED",
            latest_status_updated_on__gte=week_start
        ).count(),

        # ✅ NOW THIS WILL WORK
        "repaired_done_count": events.filter(
            latest_status="CLOSED").count(),

        # Latest rows
        "latest_events_details": event_data,
    }
