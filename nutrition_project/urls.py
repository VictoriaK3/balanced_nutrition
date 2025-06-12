"""
URL configuration for nutrition_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#nutrition_project/urls.py

from django.contrib import admin
from django.urls import path, include
from users import views
from django.shortcuts import redirect
from nutrition import views as nutrition_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', include('main.urls', namespace='main')),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
   # path('', lambda request: redirect('register')),
    path('update_weight/', nutrition_views.update_weight_view, name='update_weight'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('nutrition.urls')),

    
    # Пренасочваме коренния URL към избора на хранене
    path('', RedirectView.as_view(pattern_name='main:select_meal', permanent=False), name='home'),
      # Други приложения
    path('users/',   include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('nutrition/', include('nutrition.urls')),


   # Административен панел
    path('admin/', admin.site.urls),
]
