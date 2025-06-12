# main/urls.py
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('select-meal/',  views.select_meal,  name='select_meal'),
    path('select-foods/', views.select_foods, name='select_foods'),
    path('meal-history/', views.meal_history, name='meal_history'),
    # Регистрация на нов потребител
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]