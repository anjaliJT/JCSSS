from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import random


class Command(BaseCommand):
    help = "Seed dummy users. Usage: python manage.py createUsers --count 10"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of users to create')

    def handle(self, *args, **options):
        count = options.get('count', 10)
        User = get_user_model()

        roles = [
            "CUSTOMER",
            "CSM",
            "DIRECTOR",
            "EMP-IT",
            "EMP-STR",
            "EMP-ELE",
            "EMP-QAQC",
            "EMP-OPS",
        ]

        existing = User.objects.count()
        start_index = existing + 1

        base_phone = 7000000000  # ensure 10-digit phone numbers starting with 7

        for i in range(start_index, start_index + count):
            email = f'user{i}@example.com'
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'Skipping existing email: {email}'))
                continue

            phone_number = str(base_phone + i)
            first_name = f'User{i}'
            last_name = 'Seed'
            role = random.choice(roles)
            command_name = f'Cmd{random.randint(1,20)}'

            try:
                user = User.objects.create_user(
                    email=email,
                    password='password',
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    role=role,
                    command_name=command_name,
                )

                # make non-customers staff so they can access admin if needed
                if role != 'CUSTOMER':
                    user.is_staff = True
                    user.save()

                self.stdout.write(self.style.SUCCESS(f'Created user: {email} (role={role})'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Failed to create {email}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error for {email}: {e}'))

        self.stdout.write(self.style.SUCCESS('User seeding complete.'))
