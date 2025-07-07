from django.core.management.base import BaseCommand
from diet_ai.ml_model import train_model
from diet_ai.ml_calorie_model import train_calorie_model

class Command(BaseCommand):
    help = 'Обучава едновременно модела за режим и калориен модел'

    def handle(self, *args, **options):
        model1, _ = train_model()
        model2, _ = train_calorie_model()

        if model1 and model2:
            self.stdout.write(self.style.SUCCESS("✅ И двата модела са обучени успешно."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Един от моделите не можа да се обучи."))
