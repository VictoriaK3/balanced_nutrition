from django import template
from datetime import datetime

register = template.Library()

@register.filter
def pluck(list_of_dicts, key):
    return [d.get(key) for d in list_of_dicts]

@register.filter
def days_since(date1, date2):
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        return abs((d1 - d2).days)
    except:
        return ""

@register.filter
def index(sequence, position):
    try:
        return sequence[position - 1].weight 
    except:
        return ""