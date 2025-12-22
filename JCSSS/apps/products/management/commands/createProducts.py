from django.core.management.base import BaseCommand
from apps.products.models import Product_model, Product
from datetime import date, timedelta
import random

# Run with:
# python manage.py createProducts --count 20

class Command(BaseCommand):
    help = "Create dummy product models and products"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of products to create'
        )

    def handle(self, *args, **options):
        count = options['count']

        # Step 1: Ensure Product Models exist
        model_names = ['JF2', 'JM1', 'JM2']
        product_models = []

        for name in model_names:
            pm, created = Product_model.objects.get_or_create(model_name=name)
            product_models.append(pm)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Product_model: {name}'))

        # Step 2: Generate Products
        existing_count = Product.objects.count()
        start_index = existing_count + 1

        for i in range(start_index, start_index + count):
            tail_number = f'TN{i:04d}'

            if Product.objects.filter(tail_number=tail_number).exists():
                self.stdout.write(f'Skipped existing tail number: {tail_number}')
                continue

            manufacturing_date = date.today() - timedelta(days=random.randint(30, 900))
            delivery_date = manufacturing_date + timedelta(days=random.randint(15, 90))

            product = Product.objects.create(
                product_model=random.choice(product_models),
                tail_number=tail_number,
                order_name=f'Order {i}',
                manufecturing_Date=manufacturing_date,
                delivery_date=delivery_date,
                delivery_location=random.choice([
                    'Delhi', 'Pune', 'Bangalore', 'Hyderabad'
                ]),
                army_command=f'Command {random.randint(1, 5)}',
                unit_name=f'Unit {random.randint(1, 20)}',
                formation=f'Formation {random.randint(1, 4)}',
                warranty_period=random.choice([12, 24, 36]),
                obsolete=random.choice([False, False, False, True])  # mostly active
            )

            self.stdout.write(self.style.SUCCESS(
                f'Created Product: {product.tail_number}'
            ))

        self.stdout.write(self.style.SUCCESS('✅ Product seeding completed successfully.'))
