from django.core.management.base import BaseCommand
from eventos_app.models import (
    Category, Venue, CustomUser, Notification, Event,
    Favorito, Comment, Rating, Ticket, RefundRequest
)
from datetime import date
from django.db import transaction

class Command(BaseCommand):
    help = 'Borra todos los datos y carga un conjunto inicial para pruebas.'

    @transaction.atomic # Asegura que todas las operaciones se hagan en una sola transacción
    def handle(self, *args, **options):
        
        self.stdout.write('Borrando datos antiguos de la base de datos...')
        
        # Se borran primero los modelos que apuntan a otros.
        Favorito.objects.all().delete()
        Comment.objects.all().delete()
        Rating.objects.all().delete()
        Ticket.objects.all().delete()
        RefundRequest.objects.all().delete()
        Event.objects.all().delete()
        Notification.objects.all().delete()
        CustomUser.objects.all().delete()
        Venue.objects.all().delete()
        Category.objects.all().delete()
        
        self.stdout.write('Creando datos iniciales...')

        # Categorías
        musica = Category.objects.create(name="Música", description="Eventos musicales")
        tecnologia = Category.objects.create(name="Tecnología", description="Conferencias de tecnología")
        teatro = Category.objects.create(name="Teatro", description="Obras de teatro en vivo")
        conferencia = Category.objects.create(name="Teatro", description="Conferencias")

        
        #lugares
        luna_park = Venue.objects.create(name="Luna Park", address="Av. Madero 420", city="Buenos Aires", capacity=10000, contact="info@lunapark.com")
        teatro_colon = Venue.objects.create(name="Teatro Colón", address="Cerrito 628", city="Buenos Aires", capacity=2500, contact="contacto@colon.org.ar")
        
        
        admin_user = CustomUser.objects.create_superuser(
            username="Grupo4",
            email="admin@eventos.com",
            password="1234",
            rol="ADMIN"
        )

      
        Notification.objects.create(title="Bienvenido", message="Gracias por unirte", priority="LOW", user=admin_user)
        Notification.objects.create(title="Novedades", message="Nuevos eventos disponibles", priority="MEDIUM", user=admin_user)

        Event.objects.create(
            title="Concierto de Rock",
            description="Banda en vivo tocando grandes éxitos",
            date=date(2025, 7, 1),
            price=5000,
            categoria=musica,
            venue=luna_park,
            id_img="18IJBal9GtJJDCs5pmYkCEcZ-LyVvO78i",
            total_rating=0,        
            suma_puntaje=False,   
            cantidad_puntos=0,     
            cancelado=False        
        )
        
        Event.objects.create(
            title="Conferencia de Inteligencia Artificial",
            description="Charlas de expertos en IA",
            date=date(2025, 8, 15),
            price=8000,
            categoria=tecnologia, 
            venue=teatro_colon,
            id_img="1ep9auYAfIXmRqNUWx1zRmLvhjmbjuqQH",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        
        Event.objects.create(
            title="Obra de Teatro: Hamlet",
            description="Una puesta clásica del drama de Shakespeare",
            date=date(2025, 6, 20),
            price=3000,
            categoria=teatro,
            venue=teatro_colon,
            id_img="1FXlSy1jON88Wd2Pa3-uRbFVo9JzdaMXD",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )

        Event.objects.create(
            title="Conferencia sobre Biodiversidad",
            description="El doctor José Hernandez nos presenta su tesis sobre biodiversidad",
            date=date(2025, 6, 12),
            price=5000,
            categoria=conferencia,
            venue=luna_park,
            id_img="17im6Xdq54mv5JHEeaCot5EIBjWBdiXyR/view",
            total_rating=0,        
            suma_puntaje=False,   
            cantidad_puntos=0,     
            cancelado=False        
        )

        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales cargados correctamente.'))