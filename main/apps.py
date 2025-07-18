from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
  
    def ready(self):
        print("[DEBUG] Main signals loaded")
        import main.signals