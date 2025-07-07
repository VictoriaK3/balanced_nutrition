from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm
from .models import UserProfile
from nutrition.utils import calculate_daily_deficit, calculate_daily_water
from nutrition.models import DailyDeficit
from django.utils import timezone
from .emails import send_welcome_email

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()      
            send_welcome_email(user)             
            profile = UserProfile.objects.create(
                user           = user,
                weight         = form.cleaned_data["weight_kg"],
                height         = form.cleaned_data["height_cm"],
                age            = form.cleaned_data["age"],
                gender         = form.cleaned_data["sex"],
                activity_level = form.cleaned_data["activity_level"],
                wish_weight    = float(form.cleaned_data["weight_kg"]),
                goal           = form.cleaned_data["goal"],
                goal_date      = form.cleaned_data["goal_date"],   
            )
            kcal, p, c, f = calculate_daily_deficit(profile)

            water = calculate_daily_water(
                weight=profile.weight,
                age=profile.age,
                activity_level=profile.activity_level,
                city=profile.city
            )

            DailyDeficit.objects.update_or_create(
                user=user,
                date=timezone.now().date(),
                defaults={
                    'calorie_deficit': kcal,
                    'protein_deficit': p,
                    'carbs_deficit': c,
                    'fats_grams': f,
                    'daily_water_goal': water,
                    'city': profile.city,
                }
            )
            

            login(request, user)                  
            return redirect("main:home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or 'main:home'
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("main:home")



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from .models import UserProfile, WeightLog

@login_required
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            changed = form.changed_data

            old_db_profile = UserProfile.objects.get(user=request.user)
            old_weight = old_db_profile.weight
            old_wish_weight = old_db_profile.wish_weight
            
            updated = form.save(commit=False)
            new_weight = updated.weight
            new_wish_weight = updated.wish_weight
            changed = form.changed_data

            if "weight" in changed or "wish_weight" in changed:
              if old_weight != new_weight:
                WeightLog.objects.create(
                    user_profile=profile,
                    old_weight=old_weight,
                    new_weight=new_weight,
                    old_wish_weight=old_wish_weight,
                    new_wish_weight=new_wish_weight,
                )

            updated.save()

            # Проверяваме дали трябва да преизчислим
            if any(field in changed for field in ["weight", "wish_weight","height", "city"]):
                kcal, prot, carbs, fats = calculate_daily_deficit(updated)
                water = calculate_daily_water(
                    weight=updated.weight,
                    age=updated.age,
                    activity_level=updated.activity_level,
                    city=updated.city
                )

                DailyDeficit.objects.update_or_create(
                    user=request.user,
                    date=timezone.localdate(),
                    defaults={
                        'calorie_deficit': kcal,
                        'protein_deficit': prot,
                        'carbs_deficit': carbs,
                        'fats_grams': fats,
                        'daily_water_goal': water,
                        'city': updated.city
                    }
                )

            return redirect("main:profile")

    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "main/edit_profile.html", {"form": form})



