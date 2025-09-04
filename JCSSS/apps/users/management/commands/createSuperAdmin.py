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

        if not User.objects.filter(email="jims@johnnette.com").exists():
            superadmin = User.objects.create_superuser(
                email='jims@johnnette.com',
                password=password,
                first_name='Super',
                last_name='Admin',
                # role=admin_role,
                # department=default_department,
            )

            self.stdout.write(self.style.SUCCESS('✅ Superadmin created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Superadmin already exists.'))
