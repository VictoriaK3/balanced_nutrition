# функции – калкулации
from .models import  DailyDeficit, Food
from datetime import datetime
from django.utils import timezone
from users.models import UserProfile

def calculate_daily_deficit(profile, weight=None):

    #  Тегло и ръст винаги като float
    w = float(weight) if weight is not None else float(profile.weight)
    h = float(profile.height)

    #  BMR (Mifflin–St Jeor)
    if profile.gender == 'male':
        bmr = 10 * w + 6.25 * h - 5 * profile.age + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * profile.age - 161

    # TDEE
    factor = profile.activity_factor        
    maintenance = bmr * factor

    # Калориен баланс
    if profile.goal == 'lose_weight':
        kcal = maintenance - 500
    elif profile.goal == 'gain_weight':
        kcal = maintenance + 500
    else:
        kcal = maintenance

    # Макроси
    protein = round(w * 2)
    fats    = round(kcal * 0.25 / 9)
    carbs   = round((kcal - (protein * 4 + fats * 9)) / 4)

    return round(kcal), protein, carbs, fats


def get_last_progress_or_dailydeficit(user_profile):
    #  вземене последния запис от 
    last_progress = DailyDeficit.objects.filter(user_profile=user_profile).order_by('-date_recorded').first()
    
    if last_progress:
        return last_progress
    
    else:
         return None  

def update_user_weight(user_profile, new_weight):

    today = timezone.localdate()
     
    last_progress = DailyDeficit.objects.filter(user_profile=user_profile).order_by('-date_recorded').first()

    # Ако няма предишен запис - първи запис 
    if not last_progress:
        calories, protein, carbs, fats = calculate_daily_deficit(user_profile, new_weight)
    else:
        days_passed = (datetime.now().date() - last_progress.date_recorded).days or 1
        if days_passed == 0:
            days_passed = 1  

        # Промяна в теглото от последния запис
        weight_diff = new_weight - last_progress.weigh
        calories_change_per_day = (weight_diff * 7700) / days_passed
        adjusted_calories = max(last_progress.calories + calories_change_per_day, 1200)

        min_calories = 1200  #минимални калории, да не пада под това
        if adjusted_calories < min_calories:
            adjusted_calories = min_calories

        protein = new_weight * 2
        fats = adjusted_calories * 0.25 / 9
        carbs = (adjusted_calories - (protein * 4 + fats * 9)) / 4

        protein = round(new_weight * 2, 1)
        fats = round(adjusted_calories * 0.25 / 9, 1)
        carbs = round((adjusted_calories - (protein * 4 + fats * 9)) / 4, 1)
        calories = int(adjusted_calories)

    DailyDeficit.objects.update_or_create(
        user_profile=user_profile,
        date_recorded=today,
        defaults={
            'total_calories': calories,
            'protein_deficit': protein,
            'carbs_deficit': carbs,
            'fats_deficit': fats
        }
    )

    # Актуализираме профила
    user_profile.weight = new_weight
    user_profile.save()

    return calories, protein, carbs, fats

MEAL_SHARE = {
    "breakfast": 0.20,  
    "lunch":     0.35,  
    "snack":     0.15,  
    "dinner":    0.30,  
}
#Функция за изчисление на количествата за избрани храни
def calculate_meal_quantities(profile: UserProfile, meal_code: str, food_ids: list):
    deficit = get_current_deficit(profile.user)
    if not deficit:
        raise ValueError("Липсват данни за дневен дефицит.")

    C_daily = deficit.calorie_deficit
    P_daily = deficit.protein_deficit
    Cb_daily = deficit.carbs_deficit
    F_daily = deficit.fats_grams

    if not C_daily:
        raise ValueError("Моля, обнови профила – няма дневен дефицит.")

    #  таргети за това хранене
    portion = MEAL_SHARE.get(meal_code, 0.25)
    C_meal   = C_daily * portion
    P_meal   = P_daily * portion
    Cb_meal  = Cb_daily * portion
    F_meal   = F_daily * portion

    # данни за храните
    foods = Food.objects.filter(id__in=food_ids)
    scored = []
    for f in foods:
        dk = f.energy_kcal / 100.0
        dp = f.protein_g   / 100.0
        dc = f.carbs_g     / 100.0
        df = f.fat_g       / 100.0
     
        score = dp*P_meal + dc*Cb_meal + df*F_meal
        scored.append((f, dk, dp, dc, df, score))

    total_score = sum(s for *_, s in scored) or 1.0

    
    plan = []
    for f, dk, dp, dc, df, score in scored:
        share = score / total_score
        grams = round((C_meal * share) / dk, 1)
        kcal    = round(grams * dk, 1)
        protein = round(grams * dp, 1)
        carbs   = round(grams * dc, 1)
        fats    = round(grams * df, 1)
        plan.append({
            "food":    f,
            "grams":   grams,
            "kcal":    kcal,
            "protein": protein,
            "carbs":   carbs,
            "fats":    fats,
        })

    return plan


def calc_daily_targets(weight, height, age, gender, activity_level, goal):
   

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


import requests

def get_current_temperature(lat: float, lon: float) -> float | None:
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }
    try:
        r = requests.get(url, params=params, timeout=3)
        r.raise_for_status()
        data = r.json()
        return data["current_weather"]["temperature"]
    except (requests.RequestException, KeyError):
        return None

import requests

def get_temperature(city):
        try:
            geo = requests.get(
                'https://geocoding-api.open-meteo.com/v1/search',
                params={'name': city, 'count': 1},
                timeout=3
            ).json()
            results = geo.get('results') or []
            if not results:
                return None
            lat = results[0]['latitude']
            lon = results[0]['longitude']

            weather = requests.get(
                'https://api.open-meteo.com/v1/forecast',
                params={
                    'latitude': lat,
                    'longitude': lon,
                    'daily': 'temperature_2m_max',
                    'timezone': 'auto'
                },
                timeout=3
            ).json()
            return weather["daily"]["temperature_2m_max"][0]
        except Exception:
            return None
        
def calculate_daily_water(weight, age, activity_level, city):
    temp_c = get_temperature(city)
    print(f"[DEBUG] Temp in {city} = {temp_c}")

    #базово изчисление (30 ml / kg)
    base_ml = float(weight) * 30

    if age >= 55:
        base_ml += 200

    
    activity_levels = {
        'low': 0.00,
        'moderate': 0.10,
        'high': 0.20,
    }
    activity_coeff = activity_levels.get(activity_level, 0)

    climate_coeff = 0.15 if temp_c and temp_c > 25 else 0.0

    total_ml = float(base_ml) * (1 + activity_coeff + climate_coeff)

    return round(total_ml / 1000, 2)

from .models import DailyDeficit

def get_current_deficit(user):
    return DailyDeficit.objects.filter(user=user).order_by('-date').first()
