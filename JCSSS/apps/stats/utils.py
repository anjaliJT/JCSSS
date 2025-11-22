from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied

def check_user_permission(user, required_group):
    # ✅ Allow if user is superuser or staff
    if user.is_superuser or user.is_staff:
        return

    # ✅ Check if user belongs to the required group (case-insensitive)
    if not user.groups.filter(name__iexact=required_group).exists():
        raise PermissionDenied(f"Permission Denied.")