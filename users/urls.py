# users/urls.py
from django.urls import path
from . import views
#from nutrition.views import update_weight_view
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('register')),  # това е нов ред
    path('register/', views.register_view, name='register'),
    path("login/",    views.login_view,    name="login"),
    path("logout/",   views.logout_view,   name="logout"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
]
