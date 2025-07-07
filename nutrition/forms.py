# nutrition/forms.py

from django import forms
from .models import WaterLog
from nutrition.models import Food

class UpdateWeightForm(forms.Form):
    new_weight = forms.FloatField(label="Ново тегло (kg)")

class WaterLogForm(forms.ModelForm):
    amount_ml = forms.IntegerField(
        label="Количество (ml)",
        min_value=50,
        max_value=5000,
        initial=200,
        widget=forms.NumberInput(attrs={
            "placeholder": "напр. 200",
            "class": "form-input"
        })
    )

    class Meta:
        model = WaterLog
        fields = ['amount_ml']

#за въвеждане на храна от потребителя:
class FoodCreateForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['food_name', 'energy_kcal', 'protein_g', 'fat_g', 'carbs_g', 'category', 'vitamins_total']
        widgets = {
            'food_name': forms.TextInput(attrs={'placeholder': 'напр. Печен патладжан'}),
            'category': forms.TextInput(attrs={'placeholder': 'напр. Зеленчуци'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-gray-300 rounded px-3 py-2'
            })

class AddFoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['food_name', 'energy_kcal', 'protein_g', 'fat_g', 'carbs_g', 'category', 'vitamins_total']
        labels = {
            'food_name': 'Име на храната',
            'energy_kcal': 'Калории (на 100 г)',
            'protein_g': 'Протеини (g)',
            'fat_g': 'Мазнини (g)',
            'carbs_g': 'Въглехидрати (g)',
            'category': 'Категория',
            'vitamins_total': 'Витамини (общо)',
        }
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-input'}),
            'energy_kcal': forms.NumberInput(attrs={'class': 'form-input'}),
            'protein_g': forms.NumberInput(attrs={'class': 'form-input'}),
            'fat_g': forms.NumberInput(attrs={'class': 'form-input'}),
            'carbs_g': forms.NumberInput(attrs={'class': 'form-input'}),
            'category': forms.TextInput(attrs={'class': 'form-input'}),
            'vitamins_total': forms.NumberInput(attrs={'class': 'form-input'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Задължителни полета
        self.fields['food_name'].required = True
        self.fields['energy_kcal'].required = True
        self.fields['protein_g'].required = True
        self.fields['fat_g'].required = True
        self.fields['carbs_g'].required = True
        self.fields['category'].required = True
        self.fields['vitamins_total'].required = False