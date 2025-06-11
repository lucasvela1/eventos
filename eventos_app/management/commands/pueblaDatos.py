# eventos_app/management/commands/pueblaDatos.py

from django.core.management.base import BaseCommand
from eventos_app.models import Category, Venue, CustomUser, Notification, Event
from datetime import date
from django.db import transaction

class Command(BaseCommand):
    help = 'Carga datos iniciales en la base de datos si está vacía'

    @transaction.atomic # Asegura que todas las operaciones se hagan en una sola transacción
    def handle(self, *args, **options):
       # if Category.objects.exists() or Event.objects.exists(): #Si ya hay datos en la base de datos, no se hace nada
        #    self.stdout.write(self.style.WARNING('La base de datos ya contiene datos. No se realizó ninguna acción.'))
          #  return
        
        #El borrado es por las dudas, por si quedó alguna basura, algún dato suelto, etc
        self.stdout.write('Borrando datos antiguos (si los hubiera)...')
        Event.objects.all().delete() 
        CustomUser.objects.all().delete()
        Notification.objects.all().delete()
        Venue.objects.all().delete()
        Category.objects.all().delete()
        
        self.stdout.write('Creando datos iniciales...')

        #Categorías
        musica = Category.objects.create(name="Música", description="Eventos musicales")
        tecnologia = Category.objects.create(name="Tecnología", description="Conferencias de tecnología")
        teatro = Category.objects.create(name="Teatro", description="Obras de teatro en vivo")

        #Venues
        luna_park = Venue.objects.create(name="Luna Park", address="Av. Madero 420", city="Buenos Aires", capacity=10000, contact="info@lunapark.com")
        teatro_colon = Venue.objects.create(name="Teatro Colón", address="Cerrito 628", city="Buenos Aires", capacity=2500, contact="contacto@colon.org.ar")
        
        #Notificaciones
        notif1 = Notification.objects.create(title="Bienvenido", message="Gracias por unirte", priority="LOW")
        notif2 = Notification.objects.create(title="Novedades", message="Nuevos eventos disponibles", priority="MEDIUM")

        #Usuarios
        CustomUser.objects.create_superuser(
            username="Grupo4",
            email="admin@eventos.com",
            password="1234",
            rol="ADMIN",
            #notification=notif1
        )

        #Eventos
        Event.objects.create(
            title="Concierto de Rock",
            description="Banda en vivo tocando grandes éxitos",
            date=date(2025, 7, 1),
            price=5000,
            categoria=musica,  # Usa las variables que creaste
            venue=luna_park,
            id_img="18IJBal9GtJJDCs5pmYkCEcZ-LyVvO78i"
        )
        Event.objects.create(
            title="Conferencia de Inteligencia Artificial",
            description="Charlas de expertos en IA",
            date=date(2025, 8, 15),
            price=8000,
            categoria=tecnologia,
            venue=teatro_colon,
            id_img="1ep9auYAfIXmRqNUWx1zRmLvhjmbjuqQH"
        )
        Event.objects.create(
            title="Obra de Teatro: Hamlet",
            description="Una puesta clásica del drama de Shakespeare",
            date=date(2025, 6, 20),
            price=3000,
            categoria=teatro,
            venue=teatro_colon,
            id_img="1FXlSy1jON88Wd2Pa3-uRbFVo9JzdaMXD"
        )

        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales cargados correctamente.'))