# main/forms.py
from django import forms
from users.models import MealType
from users.models import Food

class MealSelectionForm(forms.Form):
    """
    Форма за избор на тип хранене (закуска, обяд, вечеря)
    Използва модел MealType от приложението users.
    """
    meal_type = forms.ModelChoiceField(
        queryset=MealType.objects.all(),
        label='Избери хранене',
        widget=forms.RadioSelect
    )

class FoodSelectionForm(forms.Form):
    """
    Форма за избор на хранителни продукти
    Използва модел Food от приложението users.
    """
    foods = forms.ModelMultipleChoiceField(
        queryset=Food.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Избери храни'
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
