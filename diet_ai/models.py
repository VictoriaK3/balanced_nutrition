from django.db import models

# Create your models here.
from django.db import models

class UserDietHistory(models.Model):
    age = models.PositiveSmallIntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    sex = models.CharField(max_length=10)
    goal = models.CharField(max_length=20)
    activity = models.CharField(max_length=20)
    recommended_diet = models.CharField(max_length=50)

    initial_weight = models.FloatField()
    final_weight = models.FloatField()
    duration_days = models.PositiveSmallIntegerField()

    waist_before = models.FloatField()
    waist_after = models.FloatField()
    hips_before = models.FloatField()
    hips_after = models.FloatField()
    chest_before = models.FloatField()
    chest_after = models.FloatField()

    food_likes = models.TextField()
    food_dislikes = models.TextField()

    diet_type_used = models.CharField(max_length=50)
    satisfaction_level = models.PositiveSmallIntegerField()
    success = models.CharField(max_length=10)
    estimated_lean_mass = models.FloatField()
    calories_deficit = models.PositiveSmallIntegerField(null=True, blank=True)
    macro_protein = models.PositiveSmallIntegerField(null=True, blank=True)
    macro_fat = models.PositiveSmallIntegerField(null=True, blank=True)
    macro_carbs = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.sex}, {self.age}г – {self.goal} ({self.diet_type_used})"


class PredictionLog(models.Model):
    age = models.PositiveSmallIntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    sex = models.CharField(max_length=10)
    goal = models.CharField(max_length=20)
    activity = models.CharField(max_length=20)
    predicted_diet = models.CharField(max_length=50)
    feedback = models.CharField(max_length=10, blank=True, null=True)  # 'positive' или 'negative'
    created_at = models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        return f"{self.age}г | {self.sex} – {self.goal} → {self.predicted_diet}"
