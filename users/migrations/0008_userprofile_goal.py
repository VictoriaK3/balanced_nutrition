# Generated by Django 5.2.1 on 2025-05-19 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_userprofile_activity_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='goal',
            field=models.CharField(blank=True, choices=[('lose_weight', 'Отслабване'), ('maintain_weight', 'Поддържане'), ('gain_weight', 'Качване')], max_length=20, null=True),
        ),
    ]
