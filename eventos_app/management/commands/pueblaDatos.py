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
        musica = Category.objects.create(name="Música", description="Eventos musicales", id_img = "1bihHzC1USW8qMQo-hzO-nI4C6dJi_k9i")
        tecnologia = Category.objects.create(name="Tecnología", description="Conferencias de tecnología", id_img = "1Gmxz8SczAQwJQwRUsNEttApHysy16_hn")
        teatro = Category.objects.create(name="Teatro", description="Obras de teatro en vivo", id_img = "1BX--T1S4d9bQgoPQ0eq60ugGOJ8n2W65")
        conferencia = Category.objects.create(name="Teatro", description="Conferencias", id_img = "1PQ2_kGNetdUYgJXb_w3qlt6NEJygjNMy")

        
        #lugares
        luna_park = Venue.objects.create(name="Luna Park", address="Av. Madero 420", city="Buenos Aires", capacity=10000, contact="info@lunapark.com")
        teatro_colon = Venue.objects.create(name="Teatro Colón", address="Cerrito 628", city="Buenos Aires", capacity=2500, contact="contacto@colon.org.ar")
        movistar_arena = Venue.objects.create(
            name="Movistar Arena", 
            address="Humboldt 450", 
            city="Buenos Aires", 
            capacity=15000, 
            contact="info@movistararena.com"
        )
        estadio_velez = Venue.objects.create(
            name="Estadio José Amalfitani", 
            address="Av. Juan B. Justo 9200", 
            city="Buenos Aires", 
            capacity=49000, 
            contact="contacto@velezsarfield.com"
        )
        niceto_club = Venue.objects.create(
            name="Niceto Club", 
            address="Niceto Vega 5510", 
            city="Buenos Aires", 
            capacity=1000, 
            contact="info@nicetoclub.com"
        )
        konex = Venue.objects.create(
            name="Ciudad Cultural Konex", 
            address="Sarmiento 3131", 
            city="Buenos Aires", 
            capacity=3000, 
            contact="eventos@konex.org"
        )
        centro_cultural_recoleta = Venue.objects.create(
            name="Centro Cultural Recoleta", 
            address="Junín 1930", 
            city="Buenos Aires", 
            capacity=1200, 
            contact="info@centroculturalrecoleta.org"
        )
        teatro_gran_rix = Venue.objects.create(
            name="Teatro Gran Rivadavia", 
            address="Av. Rivadavia 8636", 
            city="Buenos Aires", 
            capacity=1800, 
            contact="contacto@granrivadavia.com"
        )
        quality_espacio = Venue.objects.create(
            name="Quality Espacio",
            address="Av. Cruz Roja Argentina 200",
            city="Córdoba",
            capacity=5500,
            contact="info@qualityespacio.com"
        )

        teatro_real = Venue.objects.create(
            name="Teatro Real",
            address="San Jerónimo 66",
            city="Córdoba",
            capacity=900,
            contact="contacto@teatroreal.gob.ar"
        )
        metropolitano_rosario = Venue.objects.create(
            name="Centro de Convenciones Metropolitano",
            address="Junín 501",
            city="Rosario",
            capacity=5000,
            contact="info@metropolitanorosario.com"
        )

        teatro_el_circulo = Venue.objects.create(
            name="Teatro El Círculo",
            address="Laprida 1235",
            city="Rosario",
            capacity=1600,
            contact="contacto@teatroelcirculo.com"
        )
        arena_maipu = Venue.objects.create(
            name="Arena Maipú Stadium",
            address="Emilio Civit 791",
            city="Mendoza",
            capacity=7500,
            contact="info@arenamaipu.com"
        )

        teatro_independencia = Venue.objects.create(
            name="Teatro Independencia",
            address="Chile 1184",
            city="Mendoza",
            capacity=1100,
            contact="teatro@cultura.mendoza.gov.ar"
        )
        teatro_radio_city = Venue.objects.create(
            name="Teatro Radio City",
            address="San Luis 1750",
            city="Mar del Plata",
            capacity=900,
            contact="info@teatroradiocitymdp.com"
        )

        estadio_polideportivo = Venue.objects.create(
            name="Polideportivo Islas Malvinas",
            address="Juan B. Justo 3525",
            city="Mar del Plata",
            capacity=7200,
            contact="eventos@mdq.gov.ar"
        )





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
            id_img="1U3dTrrNGjZpFnAe9oAeYSJSFSohGolo3",
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