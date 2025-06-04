from django.core.management.base import BaseCommand
from eventos_app.models import Category, Venue, CustomUser, Notification, Event
from datetime import date

class Command(BaseCommand):
    help = 'Carga datos iniciales si no existen'

    def handle(self, *args, **options):
         
        Event.objects.all().delete()
        CustomUser.objects.all().delete()
        Notification.objects.all().delete()
        Venue.objects.all().delete()
        Category.objects.all().delete()
    
    
        # Crear categorías
        Category.new("Música", "Eventos musicales")
        Category.new("Tecnología", "Conferencias de tecnología")
        Category.new("Teatro", "Obras de teatro en vivo")
        Category.new("Deportes", "Partidos y competencias deportivas")
        Category.new("Cine", "Proyecciones de películas")

        # Crear venues
        Venue.new("Luna Park", "Av. Madero 420", "Buenos Aires", 10000, "info@lunapark.com")
        Venue.new("Teatro Colón", "Cerrito 628", "Buenos Aires", 2500, "contacto@colon.org.ar")
        Venue.new("Movistar Arena", "Humboldt 450", "CABA", 15000, "info@movistararena.com")

        # Crear notificaciones
        notif1 = Notification.objects.create(title="Bienvenido", message="Gracias por unirte", priority="LOW")
        notif2 = Notification.objects.create(title="Novedades", message="Nuevos eventos disponibles", priority="MEDIUM")

        # Crear usuarios
        CustomUser.objects.create_superuser(
        username="Grupo4",
        email="admin@eventos.com",
        password="1234",  
        rol="ADMIN",          
        notification=notif1   
    )
        CustomUser.new("admin", "admin@eventos.com", notif1)
        CustomUser.objects.create_user(username="cliente1", email="cliente1@email.com", password="1234", rol="CLIENTE", notification=notif2)
        CustomUser.objects.create_user(username="cliente2", email="cliente2@email.com", password="1234", rol="CLIENTE", notification=notif1)
        CustomUser.objects.create_user(username="vendedor1", email="vendedor@email.com", password="1234", rol="VENDEDOR", notification=notif1)

        # Recuperar instancias necesarias


        # Crear eventos
        Event.objects.create(
            title="Concierto de Rock",
            description="Banda en vivo tocando grandes éxitos",
            date=date(2025, 7, 1),
            price=5000,
            total_rating=0,
            categoria=Category.objects.get(name="Música"),
            venue=Venue.objects.get(name="Luna Park"),
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False,
            id_img="18IJBal9GtJJDCs5pmYkCEcZ-LyVvO78i"
        )

        Event.objects.create(
            title="Conferencia de Inteligencia Artificial",
            description="Charlas de expertos en IA",
            date=date(2025, 8, 15),
            price=8000,
            total_rating=0,
            categoria=Category.objects.get(name="Tecnología"),
            venue=Venue.objects.get(name="Teatro Colón"),
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False,
            id_img="1ep9auYAfIXmRqNUWx1zRmLvhjmbjuqQH"
        )

        Event.objects.create(
            title="Obra de Teatro: Hamlet",
            description="Una puesta clásica del drama de Shakespeare",
            date=date(2025, 6, 20),
            price=3000,
            total_rating=0,
            categoria=Category.objects.get(name="Teatro"),
            venue=Venue.objects.get(name="Teatro Colón"),
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False,
            id_img="1FXlSy1jON88Wd2Pa3-uRbFVo9JzdaMXD"
        )

        self.stdout.write(self.style.SUCCESS("✅ Datos iniciales cargados correctamente."))
