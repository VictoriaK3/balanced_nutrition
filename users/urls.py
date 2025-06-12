# users/urls.py
from django.urls import path
from . import views
#from nutrition.views import update_weight_view
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('register')),  # това е нов ред
    path('register/', views.register, name='register'),
    path('register_success/', views.register_success, name='register_success'),
   # path('update_weight/', update_weight_view, name='update_weight'),
]
