from django import forms

ACTIVITY_LEVELS = [
    ('ниска', 'Ниска'),
    ('средна', 'Средна'),
    ('висока', 'Висока'),
]

GOALS = [
    ('отслабване', 'Отслабване'),
    ('поддържане', 'Поддържане'),
    ('качване', 'Качване'),
]

SEXES = [
    ('мъж', 'Мъж'),
    ('жена', 'Жена'),
]

class PredictionForm(forms.Form):
    age = forms.IntegerField(label='Възраст', min_value=14, max_value=100)
    weight = forms.FloatField(label='Тегло (кг)')
    height = forms.FloatField(label='Ръст (см)')
    sex = forms.ChoiceField(choices=SEXES, label='Пол')
    goal = forms.ChoiceField(choices=GOALS, label='Цел')
    activity = forms.ChoiceField(choices=ACTIVITY_LEVELS, label='Ниво на активност')


class CaloriePredictionForm(forms.Form):
    age = forms.IntegerField(label='Възраст', min_value=14, max_value=100)
    weight = forms.FloatField(label='Тегло (кг)')
    height = forms.FloatField(label='Ръст (см)')
    sex = forms.ChoiceField(choices=SEXES, label='Пол')
    goal = forms.ChoiceField(choices=GOALS, label='Цел')
    activity = forms.ChoiceField(choices=ACTIVITY_LEVELS, label='Ниво на активност')
