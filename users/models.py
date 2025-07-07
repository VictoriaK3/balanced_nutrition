from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    ACTIVITY_LEVEL_CHOICES = [
        ('none', 'Без активност'),
        ('low', '1-3 пъти седмично (ниска активност)'),
        ('medium', '3-5 пъти седмично (средна активност)'),
        ('high', '6-7 пъти седмично (висока активност)'),
        ('very_active', 'Активна работа'),
    ]
    ACTIVITY_MULTIPLIER = {      # ← вътрешна константа
        'none':        1.2,
        'low':         1.375,
        'medium':      1.55,
        'high':        1.725,
        'very_active': 1.9,
    }


    GENDER_CHOICES = [
        ('male', 'Мъж'),
        ('female', 'Жена'),
        ('other', 'Друго'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender  = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age     = models.PositiveIntegerField()
    height  = models.PositiveIntegerField(help_text="Височина в сантиметри")
    weight  = models.FloatField(help_text="Текущо тегло в кг")
    wish_weight    = models.FloatField(help_text="Желано тегло в кг",null=True, blank=True)
    activity_level = models.CharField(max_length=30, choices=ACTIVITY_LEVEL_CHOICES)
    goal_date      = models.DateField(null=True, blank=True, help_text="Дата до която иска да постигне желаното тегло")
    goal = models.CharField(
        max_length=20,
        choices=[
            ('lose_weight', 'Отслабване'),
            ('maintain_weight', 'Поддържане'),
            ('gain_weight', 'Качване')
        ],
        null=True,
        blank=True
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="Град за климатична корекция"
    )
    #property, което връща числото
    @property
    def activity_factor(self) -> float:
        return self.ACTIVITY_MULTIPLIER.get(self.activity_level, 1.2)

    
    def save(self, *args, **kwargs):
     super().save(*args, **kwargs)

    def __str__(self):
        return f"Профил на {self.user.username}"
    
class WeightLog(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='weight_logs')
    old_weight      = models.FloatField(help_text='Старо тегло в кг', null=True, blank=True)
    new_weight      = models.FloatField(help_text='Ново тегло в кг',  null=True, blank=True)
    old_wish_weight = models.FloatField(help_text='Стара целево тегло в кг', null=True, blank=True)
    new_wish_weight = models.FloatField(help_text='Ново целево тегло в кг',  null=True, blank=True)
    data_recorded= models.DateField(auto_now_add=True)
    
    @property
    def weight_delta(self):
        if self.old_weight is not None and self.new_weight is not None:
            return self.new_weight - self.old_weight
        return None

    @property
    def wish_weight_delta(self):
        if self.old_wish_weight is not None and self.new_wish_weight is not None:
            return self.new_wish_weight - self.old_wish_weight
        return None
    
    class Meta:
        ordering = ["-data_recorded"]
    def __str__(self):
        return  (
            f"{self.user_profile.user.username}: "
            f"{self.old_weight}→{self.new_weight} kg, "
            f"{self.old_wish_weight}→{self.new_wish_weight} wish @ {self.date_recorded:%Y-%m-%d}"
        )
    
class Food(models.Model):
    food_name      = models.CharField(max_length= 255, unique=True)
    energy_kcal    = models.FloatField(null=True, blank=True)
    protein_g      = models.FloatField(null=True, blank=True)
    fat_g          = models.FloatField(null=True, blank=True)
    carbs_g        = models.FloatField(null=True, blank=True)
    vitamins_total = models.FloatField(null=True, blank=True)
    category       = models.CharField(max_length= 100, default='друго')


    def __str__(self):
        return self.food_name

class MealType(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Закуска'),
        ('lunch',     'Обяд'),
        ('snack',     'Следобедна закуска'),
        ('dinner',    'Вечеря'),
    ]

    name = models.CharField(
        max_length=30,
        choices=MEAL_CHOICES,
        unique=True,
        verbose_name='Тип хранене'
    )
#създава вътрешен клас (Meta) в Django модел, който служи за описателни настройки, а не за създаване на нова таблиц
    class Meta:
        verbose_name = 'Тип хранене'
        verbose_name_plural = 'Типове хранения'

    def __str__(self):
        return self.get_name_display()


                                        