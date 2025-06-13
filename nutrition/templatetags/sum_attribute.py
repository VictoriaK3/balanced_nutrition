from django import template
register = template.Library()

@register.filter
def sum_attribute(iterable, attr):
    """
    В шаблона:  {{ plan|sum_attribute:"grams" }}
    Сумира стойността на дадено attr през всички елементи.
    """
    return sum(getattr(obj, attr, 0) for obj in iterable)
