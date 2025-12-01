from django.core.management.base import BaseCommand
from apps.products.models import Product_model, Product
from datetime import date, timedelta
import random

# run file with the command : python .\manage.py createProducts --count 20
class Command(BaseCommand):
    help = "Create dummy product models and products. Usage: python manage.py createProducts --count 10"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of products to create')

    def handle(self, *args, **options):
        count = options.get('count', 10)

        model_names = ['JF2', 'JM1', 'JM2', 'X1', 'X2']
        created_models = []

        for mn in model_names:
            pm, created = Product_model.objects.get_or_create(model_name=mn)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Product_model: {pm.model_name}'))
            created_models.append(pm)

        # Determine a starting index based on existing products to avoid collisions
        existing_count = Product.objects.count()
        start_index = existing_count + 1

        for i in range(start_index, start_index + count):
            tail = f'TN{i:04d}'
            if Product.objects.filter(tail_number=tail).exists():
                self.stdout.write(f'Skipping existing tail number: {tail}')
                continue

            pm = random.choice(created_models)
            order_name = f'Order {i}'
            # Random manufacturing date within last 24 months
            manuf_date = date.today() - timedelta(days=random.randint(30, 365 * 2))
            is_sold = random.choice([False, True])
            sold_date = (date.today() - timedelta(days=random.randint(0, 90))) if is_sold else None

            product = Product.objects.create(
                product_model=pm,
                tail_number=tail,
                order_name=order_name,
                manufecturing_Date=manuf_date,
                is_sold=is_sold,
                sold_date=sold_date,
                source_location=f'Factory {random.choice(["A", "B", "C"]) }',
                army_command=f'Command {random.randint(1,5)}',
                unit_name=f'Unit {random.randint(1,20)}',
                formation=f'Formation {random.randint(1,4)}',
                warranty_period=24,
            )

            self.stdout.write(self.style.SUCCESS(f'Created Product: {product}'))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
