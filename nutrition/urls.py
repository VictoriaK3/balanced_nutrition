# nutrition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # AJAX/JSON крайна точка за обновяване на тегло
    path('update-weight/', views.update_weight_view, name='update_weight'),
    
    # Едно URL, което показва HTML формата и обработва „Предложи грамове“
    path('enter-meal/', views.enter_meal, name='enter_meal'),
    # (във enter_meal() ти вече проверяваш за 'confirm' в POST, затова не е нужен отделен URL за „confirm“)

    # Страница за успех, ако я имаш отделно:
    # path('meal-success/', views.meal_success, name='meal_success'),
      path('progress/', views.progress_view, name='progress'),
      path('meal-success/', views.meal_success, name='meal_success'),
     
]
