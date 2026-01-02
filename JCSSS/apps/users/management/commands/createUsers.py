from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Create predefined users with fixed roles and passwords"

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            {
                "email": "rm@johnnette.com",
                "password": "RMJTPL@2026",
                "first_name": "Ram",
                "last_name": "Sarath Kumar",
                "role": "DIRECTOR",
                "group": "ViewOnly",
            },
            {
                "email": "av@johnnette.com",
                "password": "AVJTPL@2026",
                "first_name": "Abhinav",
                "last_name": "Varrey",
                "role": "CSM",
                "group":"CSM"
            },
            {
                "email": "suraj@johnnette.com",
                "password": "Suraj@2026",
                "first_name": "Suraj",
                "last_name": "Kant Tripathi",
                "role": "CSM",
                "group":"CSM"
            },
            {
                "email": "cc@johnnette.com",
                "password": "CC@2026",
                "first_name": "Cyril",
                "last_name": "Christopher",
                "role": "DIRECTOR",
                "group":"ViewOnly"
            },
            {
                "email": "pk@johnnette.com",
                "password": "ACTO@2026",
                "first_name": "Prashant",
                "last_name": "Kumar",
                "role": "DIRECTOR",
                "group":"ViewOnly"
            },
            {
                "email": "vk@johnnette.com",
                "password": "VK@2026",
                "first_name": "Vipin",
                "last_name": "Kumar",
                "role": "EMP-ELE",
                "group":"Diagnosis"
            },
            {
                "email": "gaurav@johnnette.com",
                "password": "HOD@2026",
                "first_name": "Gaurav",
                "last_name": "Maurya",
                "role": "EMP-IT",
                "group":"ViewOnly"
            },
            {
                "email": "pankaj@johnnette.com",
                "password": "Qaqc@2026",
                "first_name": "Pankaj",
                "last_name": "Yadav",
                "role": "EMP-QAQC",
                "group":"Diagnosis"
            },
            {
                "email": "procurement@johnnette.com",
                "password": "Ops@2025",
                "first_name": "Abhishek",
                "last_name": "Mishra",
                "role": "EMP-OPS",
                "group":"Inventory"
            },
            {
                "email": "ap@johnnette.com",
                "password": "Staff@123",
                "first_name": "Aman",
                "last_name": "Pal",
                "role": "EMP-ACC",
                "group":"Accounts"
            },
            {
                "email": "hariom@johnnette.com",
                "password": "Hari@2026",
                "first_name": "Hari",
                "last_name": "Om",
                "role": "EMP-ELE",
                "group":"Diagnosis"
            },
        ]

        base_phone = 7000000000

        for index, data in enumerate(users, start=1):
            email = data["email"]

            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"Skipping existing user: {email}"))
                continue

            try:
                user = User.objects.create_user(
                    email=email,
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone_number=str(base_phone + index),
                    role=data["role"],
                    command_name=f"Cmd{index}",
                )

                if data["role"] != "CUSTOMER":
                    user.is_staff = False
                    user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {email} | Role={data['role']} | Password={data['password']}"
                    )
                )

            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Integrity error for {email}: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unexpected error for {email}: {e}"))

        self.stdout.write(self.style.SUCCESS("✅ User creation completed."))
