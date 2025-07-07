# nutrition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('update-weight/', views.update_weight_view, name='update_weight'),
    path('enter-meal/', views.enter_meal, name='enter_meal'),
      path('progress/', views.progress_view, name='progress'),
      path('meal-success/', views.meal_success, name='meal_success'),
     
]
