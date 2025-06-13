from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'height', 'weight', 'gender', 'activity_level']

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Име",     required=False)
    last_name  = forms.CharField(label="Фамилия", required=False)
    email       = forms.EmailField(required=True)
    weight_kg   = forms.DecimalField(label="Тегло (кг)")
    height_cm   = forms.DecimalField(label="Ръст (см)")
    age         = forms.IntegerField(label="Години")
    sex         = forms.ChoiceField(choices=[("male", "Мъж"), ("female", "Жена")])

    #  вместо число – текстов код (‘none’, ‘low’, …) + видим етикет
    activity_level = forms.ChoiceField(
        label="Ниво на активност",
        choices=UserProfile.ACTIVITY_LEVEL_CHOICES,   # ('low', '1-3 пъти седмично …')
        widget=forms.Select(attrs={
            "class": "w-full border border-gray-300 rounded px-3 py-2"
        })
    )
    
     # казвам на Django в какъв ред да обхожда self.fields
    field_order = [
        "first_name", "last_name",
        "username", "email",
        "password1", "password2",
        "weight_kg", "height_cm", "age", "sex",
        "activity_level",
    ]

    class Meta:
        model  = User
        fields = ("username", "email", "password1", "password2",
                  "weight_kg", "height_cm", "age", "sex", "activity_level")

    # още стил за всички полета (по желание)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault(
                "class", "w-full border border-gray-300 rounded px-3 py-2"
            )


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Потребител")
    password = forms.CharField(widget=forms.PasswordInput, label="Парола")