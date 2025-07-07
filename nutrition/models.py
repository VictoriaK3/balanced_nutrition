from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile
from users.models import MealType, Food
from django.utils import timezone
# Create your models here.
class DailyDeficit(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    date            = models.DateField(default=timezone.now,unique_for_date="user")
    total_calories  = models.FloatField(default=0, help_text="Общо изядени калории днес")

    calorie_deficit = models.FloatField(help_text="Дневен калориен дефицит в kcal")
    protein_deficit = models.FloatField(help_text="Протеини в грамове")
    carbs_deficit   = models.FloatField(help_text="Въглехидрати в грамове")
    fats_grams      = models.FloatField(help_text="Мазнини в грамове")

    calculated_at = models.DateTimeField(auto_now_add=True)
    city = models.CharField(
        max_length=100, blank=True,
        help_text="Град за климатична корекция"
    )

    daily_water_goal = models.FloatField(
        default=0.0,
        help_text="Персонализирана дневна цел за вода в литри"
    )

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        

    def __str__(self):
        return f"{self.user.username} - Дефицит: {self.calorie_deficit:.0f} kcal"
    


#Представлява цяло хранене на потребителя
class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.ForeignKey(MealType, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_calories = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.meal_type} - {self.date}"

#Елемент от храненето (напр. 100 г. картофи, 120 г. пилешко и т.н.)  
class MealItem(models.Model):
    meal = models.ForeignKey(Meal, related_name='items', on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    weight_in_grams = models.FloatField()

    def total_calories(self):
        return (self.food.energy_kcal * self.weight_in_grams) / 100
    @property
    def protein_amount(self):
        return (self.food.protein_g * self.weight_in_grams) / 100

    @property
    def carbs_amount(self):
        return (self.food.carbs_g * self.weight_in_grams) / 100

    @property
    def fats_amount(self):
        return (self.food.fat_g * self.weight_in_grams) / 100
    
class WaterLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount_ml = models.PositiveIntegerField(
    default=0,
    help_text="Изпито количество вода (в ml)"
)


    class Meta:
        unique_together = ('user', 'date')  