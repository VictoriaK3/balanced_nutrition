# main/urls.py
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),                   # /            → начален екран
    path("select-meal/", views.select_meal, name="select_meal"),   # /select-meal/
    path("select-foods/", views.select_foods, name="select_foods"),# /select-foods/
    path("dashboard/", views.dashboard, name="dashboard"),   # таблото
    path("profile/",   views.profile_view, name="profile"),   # профилът
]
