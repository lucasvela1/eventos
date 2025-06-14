from django.core.management.base import BaseCommand
from eventos_app.models import (
    Category, Venue, CustomUser, Notification, Event,
    Favorito, Comment, Rating, Ticket, RefundRequest
)
from datetime import date
from django.utils.timezone import now
from django.db import transaction
import uuid

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
        
        # Crear Usuarios
        admin_user = CustomUser.objects.create_superuser(
            username="Grupo4",
            email="admin@eventos.com",
            password="1234",
            rol="ADMIN"
        )
        vendedor1 = CustomUser.objects.create_user(
            username="vendedor1",
            email="vendedor1@eventos.com",
            password="1234",
            rol="VENDEDOR"
        )

        vendedor2 = CustomUser.objects.create_user(
            username="vendedor2",
            email="vendedor2@eventos.com",
            password="1234",
            rol="VENDEDOR"
        )
        cliente1 = CustomUser.objects.create_user(
            username="cliente1",
            email="cliente1@eventos.com",
            password="1234",
            rol="CLIENTE"
        )

        cliente2 = CustomUser.objects.create_user(
            username="cliente2",
            email="cliente2@eventos.com",
            password="1234",
            rol="CLIENTE"
        )

        cliente3 = CustomUser.objects.create_user(
            username="cliente3",
            email="cliente3@eventos.com",
            password="1234",
            rol="CLIENTE"
        )

      
        Notification.objects.create(title="Bienvenido", message="Gracias por unirte", priority="LOW", user=admin_user)
        Notification.objects.create(title="Novedades", message="Nuevos eventos disponibles", priority="MEDIUM", user=admin_user)

        evento1= Event.objects.create(
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
        
        evento2= Event.objects.create(
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
        
        evento3= Event.objects.create(
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

        evento4= Event.objects.create(
            title="Conferencia sobre Biodiversidad",
            description="El doctor José Hernandez nos presenta su tesis sobre biodiversidad",
            date=date(2025, 6, 11),
            price=5000,
            categoria=conferencia,
            venue=luna_park,
            id_img="17im6Xdq54mv5JHEeaCot5EIBjWBdiXyR",
            total_rating=0,        
            suma_puntaje=False,   
            cantidad_puntos=0,     
            cancelado=False        
        )

        evento5= Event.objects.create(
            title="Concierto de Abel Pintos",
            description="Abel Pintos en vivo tocando grandes éxitos",
            date=date(2025, 5, 1),
            price=5000,
            categoria=musica,
            venue=luna_park,
            id_img="1B5VGzF-IxZF5nHhurmOb00hZbQwaRJ7Z",
            total_rating=0,        
            suma_puntaje=True,   
            cantidad_puntos=0,     
            cancelado=False        
        )

        # Crear tickets comprados por clientes
        ticket1 = Ticket.objects.create(
            user=cliente1,
            event=evento1,
            quantity=3,
            total=4000,
            ticket_code=str(uuid.uuid4())
        )
        ticket2 = Ticket.objects.create(
            user=cliente1,
            event=evento4,
            quantity=2,
            total=4000,
            ticket_code=str(uuid.uuid4())
        )
        ticket3 = Ticket.objects.create(
            user=cliente1,
            event=evento5,
            quantity=1,
            total=4000,
            ticket_code=str(uuid.uuid4())
        )
        ticket4 = Ticket.objects.create(
            user=cliente2,
            event=evento4,
            quantity=2,
            total=4000,
            ticket_code=str(uuid.uuid4())
        )
        ticket5 = Ticket.objects.create(
            user=cliente2,
            event=evento5,
            quantity=2,
            total=4000,
            ticket_code=str(uuid.uuid4())
        )

        # Crear calificaciones
        Rating.objects.create(
            user=cliente1,
            event=evento4,
            rating=5,
            text="Un espectáculo inolvidable"
        )
        Rating.objects.create(
            user=cliente2,
            event=evento4,
            rating=3,
            text="Mucha gente"
        )

        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales cargados correctamente.'))