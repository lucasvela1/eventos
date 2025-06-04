import threading
from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos_app"
    
    ''' def ready(self):
        import eventos_app.signals  # Solo importa, no ejecuta nada aún
    '''

    def ready(self): #Es parte de la inicializacion
        # Evita que se ejecute dos veces con runserver
        if threading.current_thread().name != "MainThread":
            return #Sin esto se ejecuta dos veces

        from django.core.management import call_command #Permite ejecutar comandos como si fuera la consola
        try:
            call_command('pueblaDatos') #Llama al script que poblara con los datos iniciales
        except Exception as e:
            print(f"Error cargando datos iniciales: {e}")

       