# main/urls.py
from django.urls import path
from . import views
from users import views as uviews
from .views import progress_chart_view

app_name = "main"

urlpatterns = [
  
    path("", views.home, name="home"),  
    path(
        'select-foods/<int:meal_type_id>/',
        views.select_foods,
        name='select_foods_by_type'
    ),                
    path("select-meal/", views.select_meal, name="select_meal"),  
    path("select-foods/", views.select_foods, name="select_foods"),
    path("dashboard/", views.dashboard, name="dashboard"),  
    path("profile/",   views.profile_view, name="profile"),  
    path('accept_meal/', views.accept_meal, name='accept_meal'),
    path('public_home/', views.public_home, name='public_home'),
     path('progress/graph/', progress_chart_view, name='progress_graph'),
]
