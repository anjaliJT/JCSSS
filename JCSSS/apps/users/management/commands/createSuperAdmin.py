from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
# from apps.user.models import Role, Department

class Command(BaseCommand):
    help = 'Creates a Superadmin user'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        password = '12345'

        # Create role and department if they don't exist
        # admin_role, _ = Role.objects.get_or_create(name="SUPERADMIN")
        # default_department, _ = Department.objects.get_or_create(name="OPERATIONS")

        email = 'amir@johnnette.com'

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'phone_number':1934567890
            }
        )

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS('✅ Superadmin created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Superadmin already exists.'))
