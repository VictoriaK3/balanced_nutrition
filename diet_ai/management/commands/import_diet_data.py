import csv
from django.core.management.base import BaseCommand
from diet_ai.models import UserDietHistory

class Command(BaseCommand):
    help = 'Импортира данни от CSV файл в UserDietHistory'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Път до CSV файла')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        created = 0

        with open(csv_file, encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                UserDietHistory.objects.create(
                    age=row['age'],
                    weight=row['weight'],
                    height=row['height'],
                    sex=row['sex'],
                    goal=row['goal'],
                    activity=row['activity'],
                    recommended_diet=row['recommended_diet'],
                    initial_weight=row['initial_weight'],
                    final_weight=row['final_weight'],
                    duration_days=row['duration_days'],
                    waist_before=row['waist_before'],
                    waist_after=row['waist_after'],
                    hips_before=row['hips_before'],
                    hips_after=row['hips_after'],
                    chest_before=row['chest_before'],
                    chest_after=row['chest_after'],
                    food_likes=row['food_likes'],
                    food_dislikes=row['food_dislikes'],
                    diet_type_used=row['diet_type_used'],
                    satisfaction_level=row['satisfaction_level'],
                    success=row['success'],
                    estimated_lean_mass=row['estimated_lean_mass'],
                    calories_deficit=row['calories_deficit'],
                    macro_protein=row['macro_protein'],
                    macro_fat=row['macro_fat'],
                    macro_carbs=row['macro_carbs'],
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Успешно импортирани {created} записа.'))
