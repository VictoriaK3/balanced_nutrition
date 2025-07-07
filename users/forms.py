from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.exceptions import ValidationError
from nutrition.models import DailyDeficit
from datetime import date
from nutrition.utils import calculate_daily_water


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
    goal        = forms.ChoiceField( label="Цел",
        choices=UserProfile._meta.get_field("goal").choices,  
        widget=forms.Select(attrs={"class": "w-full border border-gray-300 rounded px-3 py-2"})
     )
    wish_weight = forms.DecimalField(label="Желано тегло (кг)")
    activity_level = forms.ChoiceField(
        label="Ниво на активност",
        choices=UserProfile.ACTIVITY_LEVEL_CHOICES,   
        widget=forms.Select(attrs={
            "class": "w-full border border-gray-300 rounded px-3 py-2"
        })
    )
    city = forms.CharField(
        label="Град",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "напр. Sofia"
        })
    )
     # казвам на Django в какъв ред да обхожда self.fields
    field_order = [
        "first_name", "last_name",
        "username", "email",
        "password1", "password2",
        "weight_kg", "height_cm", "age", "sex",
        "activity_level",
        "city",
        "goal", "wish_weight",
     
    ]
      # задължителна ЦЕЛ
    goal = forms.ChoiceField(
        label="Цел",
        choices=UserProfile._meta.get_field("goal").choices,
        widget=forms.Select()
    )
    # по желание — ЦЕЛЕВА ДАТА
    goal_date = forms.DateField(
        label="Целева дата",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    class Meta:
        model  = User
        fields = ("first_name", "last_name","username", "email", "password1", "password2",
                  "weight_kg", "height_cm", "age", "sex", "activity_level","city","goal", "wish_weight", "goal_date")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Имейл адресът вече е използван.")
        return email
    

    # още стил за всички полета (по желание)
    def __init__(self, *args, **kwargs):
     self.request = kwargs.pop("request", None)
     super().__init__(*args, **kwargs)
     for f in self.fields.values():
        f.widget.attrs.setdefault("class", "w-full border border-gray-300 rounded px-3 py-2")


def save(self, commit=True):
    user = super().save(commit=False)
    user.first_name = self.cleaned_data["first_name"]
    user.last_name  = self.cleaned_data["last_name"]
    user.email      = self.cleaned_data["email"]

    if commit:
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.weight         = self.cleaned_data["weight_kg"]
        profile.height         = self.cleaned_data["height_cm"]
        profile.age            = self.cleaned_data["age"]
        profile.gender         = self.cleaned_data["sex"]
        profile.activity_level = self.cleaned_data["activity_level"]
        profile.city           = self.cleaned_data["city"]
        profile.goal           = self.cleaned_data["goal"]
        profile.wish_weight    = self.cleaned_data["wish_weight"]
        profile.goal_date      = self.cleaned_data["goal_date"]
        profile.save()

        DailyDeficit.objects.create(
            user=user,
            date=date.today(),
            calories=profile.daily_calories,
            protein=profile.protein_target_g,
            carbs=profile.carbs_target_g,
            fats=profile.fats_target_g,
            daily_water_goal=calculate_daily_water(profile)
        )
    return user

    

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Потребител")
    password = forms.CharField(widget=forms.PasswordInput, label="Парола")


class ProfileUpdateForm(forms.ModelForm):
    weight       = forms.DecimalField(label="Текущо тегло (кг)")
    wish_weight = forms.DecimalField(label="Желано тегло (кг)")
    height      = forms.DecimalField(label="смяна на височина")
    goal_date   = forms.DateField(
        label="Целева дата",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    city = forms.CharField(
        label="Град",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full border border-gray-300 rounded px-3 py-2",
            "placeholder": "напр. Sofia"
        })
    )
    
   
    class Meta:
        model  = UserProfile
        fields = ("weight", "wish_weight", "goal_date", 'height', "city")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        for fld in self.fields.values():
            fld.widget.attrs.setdefault("class", "w-full border border-gray-300 rounded px-3 py-2")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if self.request:
                DailyDeficit.objects.create(
                    user=self.request.user,
                    date=date.today(),
                    calories=instance.daily_calories,
                    protein=instance.protein_target_g,
                    carbs=instance.carbs_target_g,
                    fats=instance.fats_target_g,
                    daily_water_goal=calculate_daily_water(instance)
                )
        return instance
     