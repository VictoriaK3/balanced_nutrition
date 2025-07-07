# main/forms.py
from django import forms
from users.models import MealType
from users.models import Food
from dal import autocomplete

class MealSelectionForm(forms.Form):
   
    meal_type = forms.ModelChoiceField(
        queryset=MealType.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Изберете тип хранене"
    )

class FoodSelectionForm(forms.Form):
    foods = forms.ModelMultipleChoiceField(
        queryset=Food.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label="Изберете храни"
    )

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Парола")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Потвърди парола")

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError("Паролите не съвпадат.")
        return cd.get('password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Потребител")
    password = forms.CharField(widget=forms.PasswordInput, label="Парола")


class MealSelectionForm(forms.Form):
    meal_type = forms.ModelChoiceField(
        queryset=MealType.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Изберете тип хранене"
    )