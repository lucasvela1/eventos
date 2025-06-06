import threading
from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos_app"
    
    ''' def ready(self):
        import eventos_app.signals  # Solo importa, no ejecuta nada aún
    '''
       