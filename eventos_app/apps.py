
from django.apps import AppConfig


class EventosAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos_app"
    
    def ready(self):
        import eventos_app.signals
       