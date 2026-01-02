# your_app/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Create default groups and assign permissions for CSM, Customer, Inventory, Diagnosis, Accounts"

    # Map group name -> list of permission codenames to assign
    # These codenames follow the django default pattern: '<action>_<modelname>'
    # e.g. 'add_event', 'view_event', 'add_repaircost', 'view_complaintstatus', etc.
    GROUP_PERMISSION_MAP = {
        "CSM": ["__ALL__"],  # special token to mean all permissions
        "Customer": [
            "add_event",
            "view_event",
            "delete_event",
            "view_complaintstatus",  # "status view"
            "change_customerpricing",  # "status view"
        ],
        "Inventory": [
            "add_repaircost",
            "view_complaintstatus",
            "add_complaintstatus",
        ],
        "Diagnosis": [
            "add_complaintstatus",
            "view_complaintstatus",
        ],
        "Accounts": [
            "add_customerpricing",
            "view_complaintstatus",
        ],
        # ✅ VIEW-ONLY GROUP
        "ViewOnly": [
            "view_event",
            "view_complaintstatus",
            "view_customerpricing",
            "view_repaircost",
            "view_customuser",
            "view_product",
        ],
    }

    def handle(self, *args, **options):
        created_groups = []
        for group_name, perms in self.GROUP_PERMISSION_MAP.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {group_name}"))
            else:
                self.stdout.write(self.style.NOTICE(f"Group already exists: {group_name}"))

            # Clear existing perms (optional) so re-running produces the same result
            group.permissions.clear()

            if "__ALL__" in perms:
                # assign all permissions
                all_perms = Permission.objects.all()
                group.permissions.set(all_perms)
                self.stdout.write(self.style.SUCCESS(f"Assigned ALL permissions to {group_name}"))
                created_groups.append(group_name)
                continue

            assigned = []
            missing = []
            for codename in perms:
                try:
                    perm = Permission.objects.get(codename=codename)
                    group.permissions.add(perm)
                    assigned.append(codename)
                except Permission.DoesNotExist:
                    # try best-effort: maybe model names differ (capitalization / singular/plural)
                    missing.append(codename)

            if assigned:
                self.stdout.write(self.style.SUCCESS(
                    f"Assigned to {group_name}: {', '.join(assigned)}"
                ))
            if missing:
                self.stdout.write(self.style.WARNING(
                    f"Missing permissions for {group_name} (check these codenames or model names): {', '.join(missing)}"
                ))

            created_groups.append(group_name)

        self.stdout.write(self.style.SUCCESS("Finished creating/updating groups."))
        self.stdout.write("Summary:")
        for g in created_groups:
            self.stdout.write(f" - {g}")
        self.stdout.write("")
        self.stdout.write("If any permissions were missing, run `python manage.py show_permissions` (see README below) to find correct codenames.")
