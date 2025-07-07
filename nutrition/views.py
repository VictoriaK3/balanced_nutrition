# nutrition/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from users.models import Food, MealType
from .models import DailyDeficit, Meal, MealItem
from .utils import update_user_weight, calculate_daily_deficit, calculate_meal_quantities
from users.models import UserProfile, WeightLog
import json

@login_required
def update_weight_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_weight = float(data.get('weight'))
        except (TypeError, ValueError, json.JSONDecodeError):
            return JsonResponse({'error': 'Невалидно тегло'}, status=400)

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Профилът не е намерен'}, status=404)

        calories, protein, carbs, fats = update_user_weight(user_profile, new_weight)
        return JsonResponse({
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats,
            'message': 'Теглото и калориите са обновени успешно!'
        })

    return JsonResponse({'error': 'Само POST метод е разрешен'}, status=405)


@login_required
def enter_meal(request):
    user = request.user
    if request.method == 'POST':
        meal_type_name = request.POST.get('meal_type')
        selected_food_ids = request.POST.getlist('food_ids')
        if not selected_food_ids:
            return render(request, 'nutrition/enter_meal.html', {
                'error': 'Моля, изберете поне една храна.',
                'foods': Food.objects.all(),
                'meal_types': MealType.objects.all(),
            })

        results = calculate_meal_quantities(user, meal_type_name, selected_food_ids)

        if 'confirm' in request.POST:
            meal_type = get_object_or_404(MealType, name=meal_type_name)
            total_kcal = sum(item['kcal'] for item in results)

            
            meal = Meal.objects.create(
                user=user,
                meal_type=meal_type,
                total_calories=total_kcal,
            )

            
            for item in results:
                MealItem.objects.create(
                    meal=meal,
                    food=item['food'],
                    weight_in_grams=item['grams']
                )

           
            today = timezone.localdate()
            daily_deficit, created = DailyDeficit.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'meal_type': meal_type,
                    'total_calories': 0,
                    'calorie_deficit': calculate_daily_deficit(user.userprofile)[0],
                    'protein_deficit': calculate_daily_deficit(user.userprofile)[1],
                    'carbs_deficit':   calculate_daily_deficit(user.userprofile)[2],
                    'fats_grams':      calculate_daily_deficit(user.userprofile)[3],
                }
            )
            # Ако не е създаден току-що, обновяваме типа хранене за справка
            if not created:
                daily_deficit.meal_type = meal_type

            
            daily_deficit.calorie_deficit -= total_kcal
            daily_deficit.protein_deficit -= sum(i['protein'] for i in results)
            daily_deficit.carbs_deficit   -= sum(i['carbs'] for i in results)
            daily_deficit.fats_grams      -= sum(i['fats'] for i in results)
            daily_deficit.total_calories  += total_kcal

            # без отрицателни стойности
            if daily_deficit.calorie_deficit < 0:
                daily_deficit.calorie_deficit = 0
            if daily_deficit.protein_deficit < 0:
                daily_deficit.protein_deficit = 0
            if daily_deficit.carbs_deficit < 0:
                daily_deficit.carbs_deficit = 0
            if daily_deficit.fats_grams < 0:
                daily_deficit.fats_grams = 0

            daily_deficit.save()
            messages.success(request, f"Храненето ({meal_type.get_name_display()}) беше записано.")
            return redirect('meal_success')

        
        return render(request, 'nutrition/confirm_meal.html', {
            'results': results,
            'meal_type': meal_type_name,
        })

    
    return render(request, 'nutrition/enter_meal.html', {
        'foods': Food.objects.all(),
        'meal_types': MealType.objects.all(),
    })


@login_required
def meal_history(request):
    user = request.user
    meals = Meal.objects.filter(user=user).order_by('-date').prefetch_related('items__food')
    return render(request, 'nutrition/meal_history.html', {'meals': meals})


@login_required
def meal_detail(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    items = meal.items.all().select_related('food')
    return render(request, 'nutrition/meal_detail.html', {
        'meal': meal,
        'items': items
    })


@login_required
def delete_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    if request.method == 'POST':
        daily = DailyDeficit.objects.filter(user=request.user, date=meal.date).first()
        if daily:
            total_kcal = meal.total_calories
            daily.calorie_deficit += total_kcal
            daily.total_calories -= total_kcal
            daily.save()
        meal.delete()
        messages.success(request, "Храненето беше изтрито успешно.")
        return redirect('meal_history')
    return render(request, 'nutrition/confirm_delete_meal.html', {'meal': meal})


@login_required
def progress_view(request):
    user = request.user
    entries = DailyDeficit.objects.filter(user=user).order_by('date')

    dates = [e.date.strftime('%Y-%m-%d') for e in entries]
    calorie_deficits = [e.calorie_deficit for e in entries]
    protein = [e.protein_deficit for e in entries]
    carbs = [e.carbs_deficit for e in entries]
    fats = [e.fats_grams for e in entries]
    water = [e.daily_water_goal for e in entries]

    context = {
        'dates': dates,
        'calories': calorie_deficits,
        'protein': protein,
        'carbs': carbs,
        'fats': fats,
        'water': water,
    }
    return render(request, 'nutrition/progress.html', context)

 
@login_required
def weight_history(request):
    user_profile = request.user.userprofile
    logs = user_profile.weight_logs.all().order_by('-data_recorded')
    return render(request, 'nutrition/weight_history.html', {'logs': logs})


@login_required
def delete_weight_log(request, log_id):
    log = get_object_or_404(WeightLog, id=log_id, user_profile=request.user.userprofile)
    if request.method == 'POST':
        log.delete()
        messages.success(request, "Записът беше изтрит успешно.")
        return redirect('weight_history')
    return render(request, 'nutrition/confirm_delete_weight_log.html', {'log': log})


@login_required
def edit_weight_log(request, log_id):
    log = get_object_or_404(WeightLog, id=log_id, user_profile=request.user.userprofile)
    if request.method == 'POST':
        form = WeightLog(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, "Записът беше актуализиран.")
            return redirect('weight_history')
    else:
        form = WeightLog(instance=log)
    return render(request, 'nutrition/edit_weight_log.html', {'form': form})


@login_required
def meal_success(request):
    return render(request, 'nutrition/meal_success.html')
