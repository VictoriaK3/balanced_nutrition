from django.contrib import admin
from .models import UserProfile, WeightLog
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(WeightLog)
#admin.site.register(MeatType)