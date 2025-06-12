from django import template
from users.models import MealType

register = template.Library()

@register.filter
def get_display_meal(meal_key):
    """
    Преобразува ключа (напр. 'breakfast') в човекочетим текст
    (напр. 'Закуска'), взет от MealType choices.
    """
    try:
        return MealType.objects.get(name=meal_key).get_name_display()
    except MealType.DoesNotExist:
        return meal_key
