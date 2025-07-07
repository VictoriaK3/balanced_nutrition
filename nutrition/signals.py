# nutrition/signals.py
import requests
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import DailyDeficit
from .utils import get_current_temperature
from nutrition.utils import calculate_daily_water

@receiver(pre_save, sender=DailyDeficit)
def fill_deficit_city_and_water_goal(sender, instance, **kwargs):
   
    if not instance.city and hasattr(instance.user, 'userprofile'):
        instance.city = instance.user.userprofile.city or ''

    temp_c = None
    if instance.city:
        try:
             geo = requests.get(
                 'https://geocoding-api.open-meteo.com/v1/search',
                  params={'name': instance.city, 'count': 1},
                  timeout=3
             ).json()
             results = geo.get('results') or []  
             if results:
                lat = results[0]['latitude']   
                lon = results[0]['longitude'] 
                temp_c = get_current_temperature(lat, lon)
        except Exception:
               temp_c = None

    if hasattr(instance.user, 'userprofile'):
     profile = instance.user.userprofile
     instance.city = profile.city

     instance.daily_water_goal = calculate_daily_water(
            weight=profile.weight,
            age=profile.age,
            activity_level=profile.activity_level,
            city=profile.city
        )
   
   
   

