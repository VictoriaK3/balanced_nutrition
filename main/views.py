# main/views.py

import json
from django.shortcuts   import render, redirect, get_object_or_404
from django.utils       import timezone
from datetime import date
from django.contrib.auth.decorators import login_required

from .forms             import MealSelectionForm, FoodSelectionForm
from users.models       import UserProfile, MealType, WeightLog
from nutrition.models   import (
    DailyDeficit, Meal, MealItem, WaterLog
)
from nutrition.utils    import calculate_meal_quantities
from django.db.models import Sum, F
from nutrition.forms import WaterLogForm
from django.utils import timezone
from nutrition.forms import FoodCreateForm
from django.contrib import messages
from datetime import date, datetime
from nutrition.utils import get_current_deficit
from nutrition.forms import AddFoodForm  

# Статични дялове от дневните калории за всяко хранене
MEAL_PORTIONS = {
    'breakfast': 0.25,
    'lunch':     0.35,
    'dinner':    0.40,
}


def home(request):
    return render(request, 'main/index.html')


@login_required
def select_meal(request):
    
    if request.method == 'POST':
        form = MealSelectionForm(request.POST)
        if form.is_valid():
            request.session['meal_type_id'] = form.cleaned_data['meal_type'].id
            return redirect('main:select_foods')
    else:
        form = MealSelectionForm()

    return render(request, 'main/select_meal.html', {'form': form})

@login_required
def select_foods_by_type(request, meal_type_id):
    # Запазване в сесията избрания тип хранене
    request.session['meal_type_id'] = meal_type_id
    # Пренасочване към стандартното select_foods
    return redirect('main:select_foods')



@login_required
def select_foods(request, meal_type_id=None):
    if meal_type_id is not None:
        request.session['meal_type_id'] = meal_type_id

    mt_id = request.session.get('meal_type_id')
    if not mt_id:
        return redirect('main:select_meal')

    meal_type = get_object_or_404(MealType, id=mt_id)
    profile = request.user.userprofile

    
    food_form = AddFoodForm()
    selection_form = FoodSelectionForm(request.POST or None)

    # Обработка на нова храна
    if request.method == 'POST':
        if 'add_food' in request.POST:
            food_form = AddFoodForm(request.POST)
            if food_form.is_valid():
                food_form.save()
                return redirect('main:select_foods')  # рефреш
        elif selection_form.is_valid():
            ids = list(selection_form.cleaned_data['foods'].values_list('id', flat=True))
            plan = calculate_meal_quantities(profile, meal_type.name, ids)
            return render(request, 'main/plan.html', {
                'plan': plan,
                'meal_type': meal_type,
            })

    return render(request, 'main/select_foods.html', {
        'form': selection_form,
        'food_form': food_form,
        'meal_type': meal_type,
    })


from django.utils import timezone

@login_required
def accept_meal(request):
    if request.method=='POST':
       
        mt_id     = request.session.get('meal_type_id')
        meal_type = get_object_or_404(MealType, id=mt_id)

        meal = Meal.objects.create(
            user           = request.user,
            meal_type      = meal_type,
            total_calories = 0,
            date           = timezone.now().date()
        )

        food_ids = request.POST.getlist('food_id')
        grams    = [float(g) for g in request.POST.getlist('grams')]

        for fid, g in zip(food_ids, grams):
            MealItem.objects.create(
                meal            = meal,
                food_id         = fid,
                weight_in_grams = g,
            )

      
        items      = meal.items.all()
        total_cal  = sum(item.total_calories() for item in items)

       
        meal.total_calories = total_cal

        meal.save()


    return redirect('main:dashboard')



@login_required
def dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    today   = date.today()
    
    water_log, _ = WaterLog.objects.get_or_create(user=request.user, date=today)
    water_form = WaterLogForm(instance=water_log)

    if request.method == 'POST' and 'water-submit' in request.POST:
     water_form = WaterLogForm(request.POST, instance=water_log)
    if water_form.is_valid():
        water_form.save()
        return redirect('main:dashboard')
    
    # Начален дневен дефицит (фиксиран в профила)
    deficit = get_current_deficit(request.user)
    initial_cal   = deficit.calorie_deficit if deficit else 0
    initial_prot  = deficit.protein_deficit if deficit else 0
    initial_carbs = deficit.carbs_deficit   if deficit else 0
    initial_fats  = deficit.fats_grams      if deficit else 0

    # Консумирани днес
    meals = Meal.objects.filter(user=request.user, date=today)
    consumed_cal   = sum(m.total_calories                  for m in meals)
    consumed_prot  = sum(item.protein_amount   for m in meals for item in m.items.all())
    consumed_carbs = sum(item.carbs_amount     for m in meals for item in m.items.all())
    consumed_fats  = sum(item.fats_amount      for m in meals for item in m.items.all())

   
    remaining_cal   = max(initial_cal   - consumed_cal,   0)
    remaining_prot  = max(initial_prot  - consumed_prot,  0)
    remaining_carbs = max(initial_carbs - consumed_carbs, 0)
    remaining_fats  = max(initial_fats  - consumed_fats,  0)
    
    deficit = DailyDeficit.objects.filter(user=request.user).order_by('-date').first()
    water_goal = deficit.daily_water_goal * 1000 if deficit else 2000


    # Подаване  трите групи: initial, consumed, remaining
    context = {
      'initial_cards': [
        {'label':'Дневен дефицит (kcal)','val': initial_cal,   'unit':'kcal'},
        {'label':'Протеин (g)',           'val': initial_prot,  'unit':'g'},
        {'label':'Въглехидрати (g)',      'val': initial_carbs,'unit':'g'},
        {'label':'Мазнини (g)',           'val': initial_fats, 'unit':'g'},
      ],
      'consumed_cards': [
        {'label':'Консумирани kcal',      'val': consumed_cal,   'unit':'kcal'},
        {'label':'Консумиран протеин',    'val': consumed_prot,  'unit':'g'},
        {'label':'Консумирани въглехидрати','val': consumed_carbs,'unit':'g'},
        {'label':'Консумирани мазнини',    'val': consumed_fats,   'unit':'g'},
      ],
      'remaining_cards': [
        {'label':'Оставащи kcal',         'val': remaining_cal,   'unit':'kcal'},
        {'label':'Оставащ протеин',       'val': remaining_prot,  'unit':'g'},
        {'label':'Оставащи въглехидрати', 'val': remaining_carbs,'unit':'g'},
        {'label':'Оставащи мазнини',      'val': remaining_fats,   'unit':'g'},
      ],
        'water_log': water_log,
        'water_form': water_form,
        'water_goal': water_goal,

    }
    
    return render(request, 'main/dashboard.html', context)

@login_required
def profile_view(request):
    
    profile = get_object_or_404(UserProfile, user=request.user)
    deficit = DailyDeficit.objects.filter(user=request.user).order_by('-date').first()

    daily_water = deficit.daily_water_goal if deficit else None

    return render(request, 'main/profile.html', {'profile': profile, "daily_water": daily_water,
        "deficit": deficit,})


@login_required
def meal_history(request):
    """
    История на въведените хранения (Meal + MealItem).
    """
    meals = Meal.objects.filter(user_profile__user=request.user).order_by('-date')
    return render(request, 'main/meal_history.html', {'meals': meals})



@login_required
def home(request):
    if not request.user.is_authenticated:
        return render(request, 'main/public_home.html')

    today = date.today()

    # 1) Зареждаме текущия дневен дефицит
    deficit = get_current_deficit(request.user)

    goal_kcal = deficit.calorie_deficit if deficit else 0
    consumed_kcal = (
        MealItem.objects
        .filter(meal__user=request.user, meal__date=today)
        .aggregate(total=Sum(F('food__energy_kcal') * F('weight_in_grams') / 100.0))
    )['total'] or 0
    rem_kcal = goal_kcal - consumed_kcal

    # 2) Макроси (пресметнати → консумирани → оставащи)
    macro_map = {
        'carbs_target_g': deficit.carbs_deficit if deficit else 0,
        'protein_target_g': deficit.protein_deficit if deficit else 0,
        'fats_target_g': deficit.fats_grams if deficit else 0,
    }

    MACRO_FIELDS = [
        ('Въглехидрати', 'carbs_g',   'carbs_target_g'),
        ('Протеин',      'protein_g', 'protein_target_g'),
        ('Мазнини',      'fat_g',     'fats_target_g'),
    ]

    macros = []
    for label, food_f, prof_f in MACRO_FIELDS:
        goal = macro_map.get(prof_f, 0)
        cons = (
            MealItem.objects
            .filter(meal__user=request.user, meal__date=today)
            .aggregate(total=Sum(F(f'food__{food_f}') * F('weight_in_grams') / 100.0))
        )['total'] or 0
        macros.append({'label': label, 'goal': goal, 'cons': cons, 'rem': goal - cons})

    # 3) Бутоните за избор на хранене
    BUTTONS = [
        ('breakfast', 'icons/breakfast.svg', 'Закуска'),
        ('lunch',     'icons/lunch.svg',     'Обяд'),
        ('dinner',    'icons/dinner.svg',    'Вечеря'),
        ('snack',     'icons/snack.svg',     'Следобедна закуска'),
    ]
    meal_links = []
    for code, icon, label in BUTTONS:
        mt = MealType.objects.get(name=code)
        meal_links.append({'id': mt.id, 'icon': icon, 'label': label})

    # 4) Хидратация
    water_log, _ = WaterLog.objects.get_or_create(user=request.user, date=today)
    water_goal = (deficit.daily_water_goal * 1000) if deficit else 2000

    if request.method == 'POST' and 'add_water_amount' in request.POST:
        try:
            add_ml = int(request.POST['add_water_amount'])
            if 0 < add_ml <= 5000:
                water_log.amount_ml += add_ml
                water_log.save()
            return redirect('main:home')
        except (ValueError, KeyError):
            pass  # игнориране на невалиден вход

    # 5) Изпращане към шаблона
    if request.user.is_authenticated:
     return render(request, 'main/home.html', {
        'kcal_card':  {'goal': goal_kcal, 'cons': consumed_kcal, 'rem': rem_kcal},
        'macros':     macros,
        'meal_links': meal_links,
        'water_log':  water_log,
        'water_goal': water_goal,
     })
    return render(request, 'main/public_home.html')



def public_home(request):
    return render(request, 'main/public_home.html')


@login_required
def add_food_view(request):
    if request.method == 'POST':
        form = FoodCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Храната беше успешно добавена!")
            return redirect('main:add_food')
    else:
        form = FoodCreateForm()

    return render(request, 'main/add_food.html', {'form': form})



# Обединено view за графика и история
@login_required
def progress_chart_view(request):
    profile = request.user.userprofile

    # Тегло по дати
    weight_logs = (
        WeightLog.objects
        .filter(user_profile=profile)
        .order_by('data_recorded')
    )

    # Калории по дати (от DailyDeficit)
    calorie_logs = DailyDeficit.objects.filter(user=request.user)

    def to_date(val):
        return val.date() if isinstance(val, datetime) else val

    deficits_by_date = {
        d.date: d.calorie_deficit  
        for d in calorie_logs
    }

    progress_data = []
    table_data = []

    prev_log = None

    for log in weight_logs:
        log_date = to_date(log.data_recorded)
        calories = deficits_by_date.get(log_date, 0)

        # За графиката
        progress_data.append({
            'date': log_date.strftime('%Y-%m-%d'),
            'weight': log.new_weight,
            'calories': calories,
        })
        
        delta_weight = round(log.new_weight - prev_log.new_weight, 1) if prev_log else None 
        
        # За таблицата
        days_diff = (log_date - to_date(prev_log.data_recorded)).days if prev_log else None
        table_data.append({
            'date': log_date.strftime('%Y-%m-%d'),
            'old_weight': prev_log.new_weight if prev_log else None,
            'new_weight': log.new_weight,
            'calories': calories,
            'days': days_diff,
            'delta': delta_weight,
        })

        prev_log = log
    
    return render(request, 'main/progress_graph.html', {
        'progress': progress_data,
        'table_data': table_data,
        
    })