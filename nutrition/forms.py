# nutrition/forms.py

from django import forms

class UpdateWeightForm(forms.Form):
    new_weight = forms.FloatField(label="Ново тегло (kg)")
