#регистрация на всички сигнали 
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile,DailyDeficit
from nutrition.utils import calculate_daily_deficit
from django.utils import timezone

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


#def save_user_profile(sender, instance, **kwargs):
 #  instance.UserProfile.save() 

def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=UserProfile)
def keep_daily_deficit(sender, instance, **kwargs):
    """
    Създава или актуализира DailyDeficit за текущия ден
    всеки път, когато UserProfile се запише (create или update).
    """
    # 1) Изчисляваме целите за деня
    calories, protein, carbs, fats = calculate_daily_deficit(instance)

    # 2) Един ред на ден → update_or_create
    DailyDeficit.objects.update_or_create(
        user=instance.user,               # сочим към auth.User!
        date=timezone.now().date(),       # ключ: (user, date)
        defaults={
            "calorie_deficit": calories,
            "protein_deficit": protein,
            "carbs_deficit": carbs,
            "fats_grams": fats,
        },
    )