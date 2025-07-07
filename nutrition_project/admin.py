from django.contrib import admin
from nutrition.models import Food, Meal, MealItem, DailyDeficit
from users.models import UserProfile, MealType, WeightLog

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'energy_kcal', 'protein_g', 'carbs_g', 'fat_g')
    search_fields = ('name',)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'date', 'total_calories')
    list_filter = ('meal_type', 'date')

@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ('meal', 'food', 'weight_in_grams')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_calories', 'protein_target_g', 'carbs_target_g', 'fats_target_g')

@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'old_weight', 'new_weight', 'data_recorded')

@admin.register(DailyDeficit)
class DailyDeficitAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'date', 'calories', 'protein_g', 'carbs_g', 'fats_g')

