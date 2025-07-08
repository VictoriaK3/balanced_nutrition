from django.core.management.base import BaseCommand
from django.utils import timezone
from nutrition.models import DailyDeficit, UserProfile
from nutrition.utils import calculate_daily_water, get_temperature

class Command(BaseCommand):
    help = "Проверява температурата и актуализира дневния воден прием, ако се е променил."

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        for profile in UserProfile.objects.all():
            city = profile.city
            if not city:
                print(f"[❌] Пропуснат потребител {profile.user.username} – няма въведен град.")
                continue

            temp = get_temperature(city)
            if temp is None:
                print(f"[⚠️] Неуспешно извличане на температура за {city}")
                continue

            new_water = calculate_daily_water(
                weight=profile.weight,
                age=profile.age,
                activity_level=profile.activity_level,
                city=city
            )
            # Опитваме да вземем последния запис, за да копираме макроси
            last_deficit = DailyDeficit.objects.filter(user=profile.user).order_by('-date').first()

            if not last_deficit:
                print(f"[❌] Пропуснат потребител {profile.user.username} – няма записан дефицит.")
                continue

            deficit, created = DailyDeficit.objects.get_or_create(
                user=profile.user,
                date=today,
                defaults={
                    "city": profile.city,
                    "daily_water_goal": new_water,
                    "calorie_deficit": last_deficit.calorie_deficit or 0,
                    "protein_deficit": last_deficit.protein_deficit or 0,
                    "carbs_deficit": last_deficit.carbs_deficit or 0,
                    "fats_grams": last_deficit.fats_grams or 0,
                }
            )

            if created:
                print(f"[✅] Създаден воден запис за {profile.user.username} – {new_water} л")
            elif round(deficit.daily_water_goal, 2) != round(new_water, 2):
                old = deficit.daily_water_goal
                deficit.daily_water_goal = new_water
                deficit.city = city
                deficit.save()
                print(f"[💧] Обновен воден прием за {profile.user.username}: {old} ➔ {new_water} л")
            else:
                print(f"[✔] Няма промяна за {profile.user.username} – остава {new_water} л")
