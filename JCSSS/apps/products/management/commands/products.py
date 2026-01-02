import pandas as pd
import re
from django.core.management.base import BaseCommand
from apps.products.models import Product, Product_model


class Command(BaseCommand):
    help = "Import products from a CSV or Excel file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="files/jf2-1.csv"
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        # ---------- Read file ----------
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, dtype=str)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path, dtype=str)
        else:
            self.stdout.write(self.style.ERROR("❌ Unsupported file type"))
            return

        # Normalize columns
        df.columns = df.columns.str.strip().str.lower()

        required_columns = [
            "tail_number",
            "model_name",
            "contract_number",
            "active_status",
            "delivery_date",
            "delivery_location",
            "warranty_period",
            "army_command",
            "unit_name",
            "formation",
        ]

        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            self.stdout.write(
                self.style.ERROR(f"❌ Missing columns: {', '.join(missing)}")
            )
            return

        created = 0
        updated = 0

        for index, row in df.iterrows():
            try:
                # Product model
                model_name = str(row.get("model_name", "")).strip()
                product_model = None
                if model_name:
                    product_model, _ = Product_model.objects.get_or_create(
                        model_name=model_name
                    )

                # Active status
                active_status = str(row.get("active_status", "")).lower() in [
                    "true", "yes", "1"
                ]

                # Delivery date
                delivery_date = None
                if pd.notna(row.get("delivery_date")):
                    delivery_date = pd.to_datetime(
                        row["delivery_date"], errors="coerce"
                    )
                    if delivery_date is not None:
                        delivery_date = delivery_date.date()

                # Warranty
                warranty_period = 24
                numbers = re.findall(r"\d+", str(row.get("warranty_period", "")))
                if numbers:
                    warranty_period = int(numbers[0])

                obj, is_created = Product.objects.update_or_create(
                    tail_number=str(row["tail_number"]).strip(),
                    defaults={
                        "product_model": product_model,
                        "contract_number": str(row["contract_number"]).strip(),
                        "active_status": active_status,
                        "delivery_date": delivery_date,
                        "delivery_location": str(row["delivery_location"]).strip(),
                        "warranty_period": warranty_period,
                        "army_command": str(row["army_command"]).strip(),
                        "unit_name": str(row["unit_name"]).strip(),
                        "formation": str(row["formation"]).strip(),
                    },
                )

                if is_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Row {index + 1} skipped: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Import complete. Created: {created}, Updated: {updated}"
            )
        )
