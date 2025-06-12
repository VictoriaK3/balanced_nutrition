# функции – калкулации
from .models import  DailyDeficit, Food
from .models import ProgressHistory
from datetime import datetime

def calculate_daily_deficit(user_profile, weight=None):
    # Ако е подадено тегло, ползвай него, иначе от профила
    w = weight if weight is not None else user_profile.weight
    if user_profile.gender == 'male':
        bmr = 10 * w + 6.25 * user_profile.height - 5 * user_profile.age + 5
    else:
        bmr = 10 * w + 6.25 * user_profile.height - 5 * user_profile.age - 161

    activity_multipliers = {
        'none': 1.2,
        'low':  1.375,
        'medium': 1.55,
        'high':   1.725,
        'very_active': 1.9,
    }

    activity_factor = activity_multipliers.get(user_profile.activity_level, 1.2)
    maintenance_calories = bmr * activity_factor

     # Целево калории в зависимост от целта
    if user_profile.goal == 'lose_weight':
       calories = maintenance_calories -500
    elif user_profile.goal == 'gain_weight':
        calories = maintenance_calories + 500
    else:
        calories = maintenance_calories

    protein = w * 2
    fats    = calories * 0.25 / 9
    carbs   = (calories -(protein * 4 + fats *9)) / 4

    return calories, protein, carbs, fats


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
def get_meal_distribution():
    # Пропорции: закуска 20%, обяд 35%, следобедна 15%, вечеря 30%
    return {
        'breakfast': 0.20,
        'lunch':     0.35,
        'snack':     0.15,
        'dinner':    0.30,
    }
    
#Функция за изчисление на количествата за избрани храни
def calculate_meal_quantities(user, meal_type_name, selected_food_ids):
     # Вземи последния дефицит за потребителя
    daily_deficit = DailyDeficit.objects.filter(user=user).latest('date')
    total_kcal = daily_deficit.calories
    total_protein = daily_deficit.protein
    total_carbs = daily_deficit.carbs
    total_fats = daily_deficit.fats

    # Разпредели според типа хранене
    distribution = get_meal_distribution()
    kcal_goal = total_kcal * distribution[meal_type_name]
    protein_goal = total_protein * distribution[meal_type_name]
    carbs_goal = total_carbs * distribution[meal_type_name]
    fats_goal = total_fats * distribution[meal_type_name]

     # Вземи избраните храни
    foods = Food.objects.filter(id__in=selected_food_ids)

    # Сумирай енергията на всички храни (на 100 г)
    total_energy = sum(food.energy_kcal for food in foods)

    results = []
    for food in foods:
        ratio = food.energy_kcal / total_energy if total_energy else 0
        kcal_share = kcal_goal * ratio

        # Колко грама от храната са нужни за тази част от калориите
        if food.energy_kcal > 0:
            grams = kcal_share * 100 / food.energy_kcal
        else:
            grams = 0

        results.append({
            'food': food,
            'grams': round(grams, 1),
            'kcal': round(food.energy_kcal * grams / 100, 1),
            'protein': round(food.protein_g * grams / 100, 1) if food.protein_g else 0,
            'carbs': round(food.carbs_g * grams / 100, 1) if food.carbs_g else 0,
            'fats': round(food.fat_g * grams / 100, 1) if food.fat_g else 0,
        })

    return results

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
