# users/views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib.auth import login
from nutrition.utils import calculate_daily_deficit

def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            # Изчисляване на калории и макронутриенти
            calculate_daily_deficit(profile)
            
            login(request, user)  # автоматично логване след регистрация
            return redirect('register_success')
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'users/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def register_success(request):
    return render(request, 'users/register_success.html')