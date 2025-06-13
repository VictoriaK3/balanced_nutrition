from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm
from .models import UserProfile


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()                     # създава User
            # създава UserProfile с допълнителните полета
            UserProfile.objects.create(
                user      = user,
                weight    = form.cleaned_data["weight_kg"],
                height    = form.cleaned_data["height_cm"],
                age       = form.cleaned_data["age"],
                gender       = form.cleaned_data["sex"],
                activity_level = form.cleaned_data["activity_level"],
                wish_weight    = float(form.cleaned_data["weight_kg"]),
            )
            login(request, user)                   # автоматичен login
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
            return redirect("main:home")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("main:home")
