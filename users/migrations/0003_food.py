# Generated by Django 5.2.1 on 2025-05-16 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_weightlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_name', models.CharField(max_length=255)),
                ('energy_kcal', models.FloatField(blank=True, null=True)),
                ('protein_g', models.FloatField(blank=True, null=True)),
                ('fat_g', models.FloatField(blank=True, null=True)),
                ('carbs_g', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
