from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.complain_form.models import Event
from apps.oem.models import ComplaintStatus
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
import random

# run file with command : python .\manage.py createComplaints --count 20
class Command(BaseCommand):
    help = "Seed dummy complaints (Event) and initial ComplaintStatus records. Usage: python manage.py createComplaints --count 10"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of complaints/events to create')

    def handle(self, *args, **options):
        count = options.get('count', 10)
        User = get_user_model()

        # Ensure a user exists to attach complaints to
        user = User.objects.filter(is_active=True).first()
        if not user:
            # create a simple seed user (CustomUser requires email and phone_number)
            try:
                user = User.objects.create_user(
                    email='seed_user@example.com',
                    password='password',
                    first_name='Seed',
                    last_name='User',
                    phone_number='0000000001',
                    role='CUSTOMER',
                    command_name='Seed'
                )
                self.stdout.write(self.style.SUCCESS('Created seed user: seed_user@example.com'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create seed user: {e}'))
                return

        serial_numbers = ['JF2', 'JM1', 'JM2', 'X1', 'X2']
        uav_types = ['JF2', 'JM1', 'JM2', 'X1', 'X2']
        # gcs_types = ['GCS-A', 'GCS-B', 'GCS-C']
        field_sites = ['Site A', 'Site B', 'Site C']
        event_types = ['Crash', 'Hard Landing', 'Loss of Control', 'Component Failure']
        damage_levels = ['Minor', 'Moderate', 'Severe']
        flight_modes = ['Manual', 'Auto', 'RTL']
        event_phases = ['Takeoff', 'Cruise', 'Landing', 'Taxi']
        damage_potentials = ['Minor', 'Moderate', 'Severe']

        existing = Event.objects.count()
        start_index = existing + 1

        for i in range(start_index, start_index + count):
            serial_number = random.choice(serial_numbers)
            tail_number = f'TN{i:04d}'
            pilot_name = f'Pilot {i}'
            email = f'pilot{i}@example.com'
            certificate_number = f'CERT{i:06d}'
            filed_by = pilot_name
            designation = 'Pilot'
            uav_type = random.choice(uav_types)
            # gcs_type = random.choice(gcs_types)
            gcs_number = f'GCS-{random.randint(100,999)}'
            uav_weight = round(random.uniform(0.5, 20.0), 2)

            days_ago = random.randint(1, 365)
            date_of_occurrence = date.today() - timedelta(days=days_ago)
            # random time
            t = time(hour=random.randint(0,23), minute=random.randint(0,59))

            field_site = random.choice(field_sites)
            event_type = random.choice(event_types)
            damage_level = random.choice(damage_levels)
            flight_mode = random.choice(flight_modes)
            event_phase = random.choice(event_phases)
            event_description = 'Auto-generated complaint for testing.'
            initial_actions_taken = 'None'
            remarks = 'Seed data'
            organization = f'Org {random.randint(1,10)}'

            wind = random.choice(['Calm', 'Breezy', 'Windy'])
            temperature = f"{random.randint(10,35)} C"
            # pressure_qnh = f"{random.randint(950,1050)} hPa"
            turbulence = random.choice([True, False])
            windshear = random.choice([True, False])
            rain = random.choice([True, False])
            icing = False
            snow = False

            damage_potential = random.choice(damage_potentials)

            # Create event
            try:
                evt = Event.objects.create(
                    pilot_name=pilot_name,
                    user=user,
                    email=email,
                    certificate_number=certificate_number,
                    filed_by=filed_by,
                    designation=designation,
                    serial_number=serial_number,
                    tail_number=tail_number,
                    uav_type=uav_type,
                    # gcs_type=gcs_type,
                    gcs_number=gcs_number,
                    uav_weight=uav_weight,
                    date_of_occurrence=date_of_occurrence,
                    time_of_occurrence=t,
                    field_site=field_site,
                    event_type=event_type,
                    damage_level=damage_level,
                    flight_mode=flight_mode,
                    event_phase=event_phase,
                    event_description=event_description,
                    initial_actions_taken=initial_actions_taken,
                    remarks=remarks,
                    organization=organization,
                    wind=wind,
                    temperature=temperature,
                    # pressure_qnh=pressure_qnh,
                    turbulence=turbulence,
                    windshear=windshear,
                    rain=rain,
                    icing=icing,
                    snow=snow,
                    damage_potential=damage_potential,
                )

                # Create initial complaint status
                ComplaintStatus.objects.create(event=evt, status='IN REVIEW', remarks='Seeded')

                self.stdout.write(self.style.SUCCESS(f'Created Event: {evt.unique_token or evt.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating event {i}: {e}'))

        self.stdout.write(self.style.SUCCESS('Seeding complaints complete.'))
