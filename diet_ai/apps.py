from django.apps import AppConfig


class DietAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diet_ai'

    def ready(self):
        # Извиква се при стартиране на сървъра
        from .ml_model import train_model
        train_model()