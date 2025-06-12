import os
import csv
from django.core.management.base import BaseCommand
from users.models import Food

class Command(BaseCommand):
    help = 'Импортира CSV файлове с храни в базата данни'

    def handle(self, *args, **kwargs):
        csv_files = [
            'data/FOOD-DATA-GROUP1.csv',
            'data/FOOD-DATA-GROUP2-BG.csv',
            'data/FOOD-DATA-GROUP3-BG.csv',
            'data/FOOD-DATA-GROUP4-BG.csv',
            'data/FOOD-DATA-GROUP5-BG.csv',
        ]

        def to_float(val):
            try:
                return float(str(val).replace(',', '.'))
            except:
                return None

        for file_path in csv_files:
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'Файлът не съществува: {file_path}'))
                continue

            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    food_name = row.get('food_name')
                    if not food_name:
                        continue

                    # Импортирай без дубликати и актуализирай ако вече съществува
                    obj, created = Food.objects.update_or_create(
                        food_name=food_name.strip(),
                        defaults={
                            'energy_kcal': to_float(row.get('Caloric Value')),
                            'protein_g': to_float(row.get('Protein')),
                            'fat_g': to_float(row.get('Fat')),
                            'carbs_g': to_float(row.get('Carbohydrates')),
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f'✅ Импортиран успешно: {file_path}'))
