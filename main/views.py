# main/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MealSelectionForm, FoodSelectionForm
from users.models import Food
from nutrition.models import Meal, MealItem

def home(request):
    return render(request, 'home.html') 

# Статични дялове от дневните калории за всяко хранене
MEAL_PORTIONS = {
    'breakfast': 0.25,  # Закуска
    'lunch':     0.35,  # Обяд
    'dinner':    0.40,  # Вечеря
}

@login_required
def select_meal(request):
    """
    Стъпка 1: Избор на тип хранене
    """
    if request.method == 'POST':
        form = MealSelectionForm(request.POST)
        if form.is_valid():
            meal_type = form.cleaned_data['meal_type']
            request.session['meal_type_id'] = meal_type.id
            return redirect('main:select_foods')
    else:
        form = MealSelectionForm()
    return render(request, 'main/select_meal.html', {'form': form})

@login_required
def select_foods(request):
    """
    Стъпка 2: Избор на храни и изчисляване на грамове
    """
    meal_type_id = request.session.get('meal_type_id')
    if not meal_type_id:
        return redirect('main:select_meal')

    # Зареждаме избрания тип хранене от DB, за да покажем име
    # Импортирайте MealType, ако трябва
    from users.models import MealType
    meal_type = MealType.objects.get(id=meal_type_id)

    if request.method == 'POST':
        form = FoodSelectionForm(request.POST)
        if form.is_valid():
            foods = form.cleaned_data['foods']

            # Взимаме дневните калории от профила на потребителя
            daily_cal = request.user.userprofile.daily_calories

            # Изчисляваме калориите за това хранене
            key = meal_type.code if hasattr(meal_type, 'code') else meal_type.name.lower()
            portion = MEAL_PORTIONS.get(key, 0)
            meal_cal = daily_cal * portion

            # Създаваме записи за Meal и MealItems
            meal_record = Meal.objects.create(
                user=request.user,
                meal_type=meal_type,
            )

            plan = []
            for food in foods:
                # Калории на 100g
                cal_per_100g = (
                    food.protein * 4 +
                    food.carb    * 4 +
                    food.fat     * 9
                )
                # Дял калории за всяка храна
                cal_share = meal_cal / len(foods)
                # Изчисляваме грамаж
                grams = cal_share / (cal_per_100g / 100)
                grams = round(grams, 1)

                # Записваме в MealItem
                MealItem.objects.create(
                    meal=meal_record,
                    food=food,
                    quantity_g=grams
                )

                plan.append({'food': food, 'grams': grams})

            return render(request, 'main/plan.html', {
                'plan': plan,
                'meal_type': meal_type,
            })
    else:
        form = FoodSelectionForm()

    return render(request, 'main/select_foods.html', {
        'form': form,
        'meal_type': meal_type,
    })

from django.contrib.auth.decorators import login_required
from nutrition.models import Meal

@login_required
def meal_history(request):
    """
    Вю за показване на историята с въведените хранения
    """
    meals = Meal.objects.filter(user=request.user).order_by('-date')
    return render(request, 'main/meal_history.html', {'meals': meals})

from django.contrib.auth import login
from users.forms import CustomUserCreationForm, UserProfileForm
def register(request):
    """
    Вю за регистрация на нов потребител + профил
    """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('main:home')
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LoginForm

def home(request):
    return render(request, 'main/index.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')
