#регистрация на всички сигнали 
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile,DailyDeficit
from nutrition.utils import calculate_daily_deficit

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


#def save_user_profile(sender, instance, **kwargs):
 #  instance.UserProfile.save() 

def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=UserProfile)
def create_daily_deficit(sender, instance, created, **kwargs):
    if created:
        calories, protein, carbs, fats = calculate_daily_deficit(instance)

         # Създаване на DailyDeficit запис
        DailyDeficit.objects.create(
            user = instance,
            calorie_deficit =calories,
            protein_deficit = protein,
            carbs_deficit = carbs,
            fats_grams = fats
        )