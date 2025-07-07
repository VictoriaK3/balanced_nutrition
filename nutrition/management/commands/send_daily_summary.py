from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.template.loader import render_to_string
from datetime import date

from nutrition.models import Meal, MealItem, DailyDeficit

User = get_user_model()


class Command(BaseCommand):
    help = 'Изпраща дневни обобщения и съвети по имейл на потребителите в 21:00'

    def handle(self, *args, **kwargs):
        today = date.today()

        for user in User.objects.all():
            meals_today = Meal.objects.filter(user=user, date=today)
            deficit = DailyDeficit.objects.filter(user=user, date=today).first()

            if not meals_today.exists():
                # Не е въвел никакво хранене
                message = (
                    f"Здравей, {user.first_name or user.username}!\n\n"
                    "Днес не си въвел нито едно хранене в системата. 🍽️\n"
                    "Не забравяй утре да въведеш храненията си, за да следиш своя прогрес. "
                    "Ние сме тук, за да ти помагаме по пътя към по-здравословен живот! 💚\n\n"
                    "С най-добри пожелания,\nЕкипът на Balanced Nutrition"
                )

                email = EmailMultiAlternatives(
                    subject="Balanced Nutrition – Напомняне за въвеждане на храна",
                    body=message,
                    from_email="no-reply@balancednutrition.bg",
                    to=[user.email]
                )
                email.send()
                self.stdout.write(f"📬 Изпратен напомнящ имейл до {user.email}")
                continue  # пропускаме останалата логика

            # Има въведени хранения
            total_kcal = 0
            total_protein = 0
            total_carbs = 0
            total_fats = 0
            food_categories = []

            for meal in meals_today:
                for item in MealItem.objects.filter(meal=meal):
                    total_kcal += item.kcal
                    total_protein += item.protein
                    total_carbs += item.carbs
                    total_fats += item.fats
                    if item.food.category:
                        food_categories.append(item.food.category.lower())

            diff = 0
            if deficit:
                target = deficit.calories
                diff = total_kcal - target
            else:
                target = None

            # Генерираме съвети
            advice_lines = []

            if total_protein < 50:
                advice_lines.append("👉 Добави повече протеин – пиле, боб, яйца.")
            if total_carbs > 200:
                advice_lines.append("👀 Внимавай с въглехидратите – замени част с повече зеленчуци.")
            if "зеленчуци" not in food_categories:
                advice_lines.append("🥦 Не виждам зеленчуци днес – утре наблегни на тях за фибри и витамини!")

            advice_text = "\n".join(advice_lines) or "✅ Продължавай в същия дух – балансът е ключът към резултата! 💪"

            # HTML имейл съдържание
            html_content = render_to_string('emails/daily_summary_email.html', {
                'name': user.first_name or user.username,
                'kcal': round(total_kcal),
                'protein': round(total_protein),
                'carbs': round(total_carbs),
                'fat': round(total_fats),
                'diff': round(diff),
                'advice': advice_text,
            })

            email = EmailMultiAlternatives(
                subject="Balanced Nutrition – Твоят дневен отчет",
                body="Здравей! Виж HTML версията на имейла, ако не виждаш пълния текст.",
                from_email="no-reply@balancednutrition.bg",
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            self.stdout.write(f"✔ Изпратен отчет до {user.email}")
