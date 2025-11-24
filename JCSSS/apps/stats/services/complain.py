from datetime import timedelta
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Exists
from apps.complain_form.models import Event
from apps.oem.models import ComplaintStatus


def compute_active_complain(user):

    # Subquery → latest status name
    latest_status = ComplaintStatus.objects.filter(
        event=OuterRef('pk')
    ).order_by('-updated_at').values('status')[:1]

    # Subquery → timestamp of latest update
    latest_status_updated_on = ComplaintStatus.objects.filter(
        event=OuterRef('pk')
    ).order_by('-updated_at').values('updated_at')[:1]

    # Subquery → check if event ever had REPAIR
    has_repair_status = ComplaintStatus.objects.filter(
        event=OuterRef('pk'),
        status__iexact="REPAIR"
    )

    # Filter events by user role
    if user.role == "CUSTOMER":
        events = Event.objects.filter(user=user)
    else:
        events = Event.objects.all()

    # Annotate computed fields
    events = events.annotate(
        latest_status=Subquery(latest_status),
        latest_status_updated_on=Subquery(latest_status_updated_on),
        had_repair_status=Exists(has_repair_status),
    )

    # Date logic for last 7 days
    today = timezone.now()
    week_start = today - timedelta(days=7)

    # 🆕 Progress calculation mapping
    event_data = []
    for e in events[:4]:
        progress_map = {
            "REVIEW": 25,
            "REPAIR": 75,
            "CLOSED": 100,
        }

        progress = progress_map.get(e.latest_status, 25)

        event_data.append({
            "model_number": e.model_number,
            "tail_number": e.tail_number,
            "current_status": e.latest_status,
            "progress": progress,
        })

    # Return final summary
    return {

        # Counts
        "total_count": events.count(),
        "open_status_count": events.exclude(latest_status__iexact="CLOSED").count(),
        "pending_status_count": events.filter(latest_status__iexact="REVIEW").count(),
        "resolved_this_week_count": events.filter(
            latest_status__iexact="CLOSED",
            latest_status_updated_on__gte=week_start
        ).count(),
        "repaired_done_count": events.filter(
            latest_status__iexact="CLOSED",
            had_repair_status=True
        ).count(),

        # 🆕 Latest 4 detailed rows
        "latest_events_details": event_data,
    }
