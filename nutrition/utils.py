# функции – калкулации
from .models import  DailyDeficit, Food
from .models import ProgressHistory
from datetime import datetime
from django.utils import timezone
from users.models import UserProfile

def calculate_daily_deficit(profile, weight=None):
    """Връща kcal, protein_g, carbs_g, fats_g."""

    # 1. Тегло и ръст винаги като float
    w = float(weight) if weight is not None else float(profile.weight)
    h = float(profile.height)

    # 2. BMR (Mifflin–St Jeor)
    if profile.gender == 'male':
        bmr = 10 * w + 6.25 * h - 5 * profile.age + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * profile.age - 161

    # 3. TDEE
    factor = profile.activity_factor        # вече е float
    maintenance = bmr * factor

    # 4. Калориен баланс
    if profile.goal == 'lose_weight':
        kcal = maintenance - 500
    elif profile.goal == 'gain_weight':
        kcal = maintenance + 500
    else:
        kcal = maintenance

    # 5. Макроси
    protein = round(w * 2)
    fats    = round(kcal * 0.25 / 9)
    carbs   = round((kcal - (protein * 4 + fats * 9)) / 4)

    return round(kcal), protein, carbs, fats


def get_last_progress_or_dailydeficit(user_profile):
    # Опитваме да вземем последния запис от ProgressHistory
    last_progress = ProgressHistory.objects.filter(user_profile=user_profile).order_by('-date_recorded').first()
    
    if last_progress:
        return last_progress
    else:
        # Ако няма запис в ProgressHistory - взимаме от DailyDeficit
        daily_deficit = DailyDeficit.objects.filter(user_profile=user_profile).order_by('-id').first()
        if daily_deficit:
            # Превръщаме DailyDeficit в "прогрес"
            return ProgressHistory(
                user_profile=user_profile,
                date_recorded=daily_deficit.date_recorded if hasattr(daily_deficit, 'date_recorded') else datetime.now(),
                weight=user_profile.weight,
                calories=daily_deficit.calories,
                protein=daily_deficit.protein,
                carbs=daily_deficit.carbs,
                fats=daily_deficit.fats
            )
        else:
            return None  # Ако няма и DailyDeficit (рядко се случва)

def update_user_weight(user_profile, new_weight):
    """
    Актуализира теглото на потребителя, изчислява калориите, макронутриентите,
    като адаптира приема спрямо метаболизма (промяна в теглото във времето).
    Записва в ProgressHistory новия запис.
    """
     # Вземаме последния запис в прогрес историята, ако има
    last_progress = ProgressHistory.objects.filter(user_profile=user_profile).order_by('-date_recorded').first()

    # Ако няма предишен запис - първи запис (взимаме стойности от DailyDeficit)
    if not last_progress:
        calories, protein, carbs, fats = calculate_daily_deficit(user_profile, new_weight)
    else:
        # Изчисляваме колко дни са минали от последния запис
        days_passed = (datetime.now() - last_progress.date_recorded).days
        if days_passed == 0:
            days_passed = 1  # За да избегнем деление на 0

        # Промяна в теглото от последния запис
        weight_diff = new_weight - last_progress.weight

        # Адаптация на калориите спрямо промяната в теглото и времето (метаболизъм)
        # 1 кг мазнини ~ 7700 калории. Ако е загубено 1 кг за 7 дни, дневен дефицит е 1100 калории.
        # Ние изчисляваме дневната калорийна разлика, като корекция към последните калории

        calories_change_per_day = (weight_diff * 7700) / days_passed

        # Новите калории се коригират спрямо предишните калории + калориите за промяната на теглото
        adjusted_calories = last_progress.calories + calories_change_per_day

        # За по-голяма персонализация, може да добавиш ограничение (напр. не по-малко от базов минимум)
        min_calories = 1200  # примерно минимални калории, да не пада под това
        if adjusted_calories < min_calories:
            adjusted_calories = min_calories

        # Пресмятаме новите макроси по адаптираните калории и новото тегло
        protein = new_weight * 2
        fats = adjusted_calories * 0.25 / 9
        carbs = (adjusted_calories - (protein * 4 + fats * 9)) / 4

        calories = int(adjusted_calories)
        protein = round(protein, 1)
        fats = round(fats, 1)
        carbs = round(carbs, 1)

    # Записваме новата история
    ProgressHistory.objects.create(
        user_profile=user_profile,
        weight=new_weight,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats
    )

    # Актуализираме профила
    user_profile.weight = new_weight
    user_profile.save()

    return calories, protein, carbs, fats

""" функции за изчисление на грамове за едно ядене
"""
#разпределяне на макронутриентите по хранения
MEAL_SHARE = {
    "breakfast": 0.20,  # 20 %
    "lunch":     0.35,  # 35 %
    "snack":     0.15,  # 15 %
    "dinner":    0.30,  # 30 %
}
#Функция за изчисление на количествата за избрани храни
def calculate_meal_quantities(user, meal_code, food_ids):
    """
    • user        – request.user
    • meal_code   – 'breakfast' | 'lunch' | 'snack' | 'dinner'
    • food_ids    – list/iterable от избраните Food PK-та

    Връща list от dict-ове:
        [{'food': Food, 'grams': 123, 'kcal': 321}, …]
    """
    # 2.2  Взимаме последния DailyDeficit → дневни kcal & макроси
    daily = (user.daily_deficits
                  .filter(date__lte=timezone.now().date())
                  .first())        # последният (благодарение на Meta.ordering)

    if not daily:
        # Ако профилът е нов и още няма дефицит – по-добре гръмни,
        # за да се сетим да създадем/обновим профила
        raise ValueError("No DailyDeficit found – създай/обнови профила първо!")

    # 2.3  Колко kcal трябва да покрием с това хранене
    target_cal = daily.calorie_deficit * MEAL_SHARE[meal_code]

    # 2.4  Зареждаме обектите Food
    foods = list(Food.objects.filter(id__in=food_ids))

    # 2.5  Изчисляваме „kcal за 1 g“ за всяка храна
    kcal_per_g = [f.calories / 100 for f in foods]   # защото calories са „на 100 g“

    # 2.6  Сборът на всички калории-на-грам → ще ни трябва за пропорцията
    total_kcal_per_g = sum(kcal_per_g)

    plan = []
    for food, kpg in zip(foods, kcal_per_g):
        share = kpg / total_kcal_per_g          # колко % от общите kcal „носи“ тази храна
        grams = round(target_cal * share / kpg) # => грамовете ѝ
        plan.append({
            "food":  food,
            "grams": grams,
            "kcal":  grams * kpg,               # реалните kcal (≈ share * target_cal)
        })

    return plan

#calc_daily_targets, която приема числови стойности (вместо user_profile) и вътре конструираме „временен профил“ _TempProfile, 
# за да може да извикаме съществуващата calculate_daily_deficit.
def calc_daily_targets(weight, height, age, gender, activity_level, goal):
    """
    Използва calculate_daily_deficit, за да върне dict:
      {
        "kcal": int,
        "protein_g": float,
        "carbs_g": float,
        "fats_g": float
      }
    """
    # Викаме вече съществуващата функция; тя връща (calories, protein, carbs, fats)
    calories, protein, carbs, fats = calculate_daily_deficit(
        user_profile=None,         # подменяме със сурови аргументи, затова подаваме None
        weight=weight,
        # height, age, gender, activity_level, goal се предават индивидуално
        # но calculate_daily_deficit приема само user_profile + weight, така че
        # ще извикаме calculate_daily_deficit по-този начин:
        # ➔ временно създаваме „mock профил“?
    )

    # За да използваме calculate_daily_deficit, тя иска обект user_profile.
    # Ще реализираме лека обвивка: ще направим вътре временен UserProfile-like обект.

    class _TempProfile:
        def __init__(self, w, h, a, gend, act, gl):
            self.weight = w
            self.height = h
            self.age = a
            self.gender = gend
            self.activity_level = act
            self.goal = gl

    temp = _TempProfile(weight, height, age, gender, activity_level, goal)
    cal, pr, cb, ft = calculate_daily_deficit(temp)

    return {
        "kcal": int(round(cal)),
        "protein_g": float(round(pr, 1)),
        "carbs_g": float(round(cb, 1)),
        "fats_g": float(round(ft, 1)),
    }
