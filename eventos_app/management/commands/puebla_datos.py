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
        conferencia = Category.objects.create(name="Conferencia", description="Conferencias", id_img = "1Pf_8mxdFBij33-dTuRhYdEErb-X-SWpg")
        pelicula = Category.objects.create(name="Pelicula", description="Peliculas", id_img = "17pW8ERXaZ6bgjsdr7QfdQ5ZTzunir916")
        deporte = Category.objects.create(name="Deporte", description="Eventos deportivos", id_img = "1LZZ-vW_Q-LtWyk-I02U8GVap0fkD0fqz")
        arte = Category.objects.create(name="Arte", description="Exposiciones de arte", id_img = "1xPjhxTF8AaVj6ZO6ugkZ4FYPBDLZ8HkT")
        literatura = Category.objects.create(name="Literatura", description="Eventos literarios", id_img = "16coPtu6AfaegS2KR2UgVt36a0vhENx-F")
        

        
        #lugares
        luna_park = Venue.objects.create(
            name="Luna Park", 
            address="Av. Madero 420", 
            city="Buenos Aires", 
            capacity=10000, 
            contact="info@lunapark.com")
        
        teatro_colon = Venue.objects.create(
            name="Teatro Colón", 
            address="Cerrito 628", 
            city="Buenos Aires", 
            capacity=2500, 
            contact="contacto@colon.org.ar")
        
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

        museo_bellas_artes = Venue.objects.create(
            name="Museo Nacional de Bellas Artes",
            address="Av. del Libertador 1473",
            city="Buenos Aires",
            capacity=1200,
            contact="info@mnba.gob.ar"
        )

        parque_centenario = Venue.objects.create(
            name="Parque Centenario",
            address="Av. Díaz Vélez al 4800",
            city="Buenos Aires",
            capacity=3000,
            contact="eventos@parquecentenario.gob.ar"
        )

        cine_gaumont = Venue.objects.create(
            name="Cine Gaumont",
            address="Av. Rivadavia 1635",
            city="Buenos Aires",
            capacity=600,
            contact="contacto@cinegaumont.com"
        )

        cinemark_palermo = Venue.objects.create(
            name="Cinemark Palermo",
            address="Beruti 3399",
            city="Buenos Aires",
            capacity=800,
            contact="info@cinemark.com.ar"
        )

        espacio_inca = Venue.objects.create(
            name="Espacio INCAA Km 0",
            address="Av. Rivadavia 1635",
            city="Buenos Aires",
            capacity=500,
            contact="info@espacioincaa.gob.ar"
        )

        facultad_filosofia = Venue.objects.create(
            name="Facultad de Filosofía y Letras - UBA",
            address="Puán 480",
            city="Buenos Aires",
            capacity=1000,
            contact="eventos@filo.uba.ar"
        )

        balcarce_tenis = Venue.objects.create(
            name="Club de Tenis Balcarce",
            address="Av. del Deporte s/n",
            city="Balcarce",
            capacity=1500,
            contact="info@clubbalcarce.com"
        )

        predio_la_rural = Venue.objects.create(
            name="La Rural - Predio Ferial de Buenos Aires",
            address="Av. Sarmiento 2704",
            city="Buenos Aires",
            capacity=10000,
            contact="info@larural.com.ar"
        )

        facultad_ingenieria = Venue.objects.create(
            name="Facultad de Ingeniería - UBA",
            address="Av. Paseo Colón 850",
            city="Buenos Aires",
            capacity=1500,
            contact="eventos@fi.uba.ar"
        )

        hotel_sheraton = Venue.objects.create(
            name="Sheraton Buenos Aires Hotel & Convention Center",
            address="San Martín 1225",
            city="Buenos Aires",
            capacity=2500,
            contact="info@sheratonbuenosaires.com"
        )

        biblioteca_nacional = Venue.objects.create(
            name="Biblioteca Nacional Mariano Moreno",
            address="Agüero 2502",
            city="Buenos Aires",
            capacity=1200,
            contact="info@bn.gov.ar"
        )

        cafe_literario = Venue.objects.create(
            name="Café Literario El Gato Negro",
            address="Av. Corrientes 1669",
            city="Buenos Aires",
            capacity=150,
            contact="contacto@gatonegro.com.ar"
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
            venue=luna_park,
            id_img="18IJBal9GtJJDCs5pmYkCEcZ-LyVvO78i",
            total_rating=0,        
            suma_puntaje=False,   
            cantidad_puntos=0,     
            cancelado=False        
        )
        evento1.categorias.add(musica)
        
        evento2= Event.objects.create(
            title="Conferencia de Inteligencia Artificial",
            description="Charlas de expertos en IA",
            date=date(2025, 8, 15),
            price=8000,
            venue=teatro_colon,
            id_img="1-N4UiGcoyA-Mn3K6Ha-IOsdnYUoBoKgR",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento2.categorias.add(tecnologia)
        
        evento3= Event.objects.create(
            title="Obra de Teatro: Hamlet",
            description="Una puesta clásica del drama de Shakespeare",
            date=date(2025, 6, 20),
            price=3000,
            venue=teatro_colon,
            id_img="1FXlSy1jON88Wd2Pa3-uRbFVo9JzdaMXD",
            total_rating=0,
            suma_puntaje=True,
            cantidad_puntos=5000,
            cancelado=False
        )
        evento3.categorias.add(teatro)

        evento4= Event.objects.create(
            title="Conferencia sobre Biodiversidad",
            description="El doctor José Hernandez nos presenta su tesis sobre biodiversidad",
            date=date(2025, 6, 11),
            price=5000,
            venue=luna_park,
            id_img="17im6Xdq54mv5JHEeaCot5EIBjWBdiXyR",
            total_rating=0,        
            suma_puntaje=False,   
            cantidad_puntos=0,     
            cancelado=False        
        )
        evento4.categorias.add(conferencia)

        evento5= Event.objects.create(
            title="Concierto de Abel Pintos",
            description="Abel Pintos en vivo tocando grandes éxitos",
            date=date(2025, 10, 1),
            price=5000,
            venue=luna_park,
            id_img="1U3dTrrNGjZpFnAe9oAeYSJSFSohGolo3",
            total_rating=0,        
            suma_puntaje=True,   
            cantidad_puntos=1200,     
            cancelado=False        
        )
        evento5.categorias.add(musica)

        evento6 = Event.objects.create(
            title="Festival Arte Urbano",
            description="Exposición de arte callejero con intervenciones en vivo.",
            date=date(2025, 6, 5),
            price=2000,
            venue=centro_cultural_recoleta,
            id_img="1-heBQdr_JseyZHpuEmCRYa4AJlJ0jNUW", 
            total_rating=3,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento6.categorias.add(arte)

        evento7 = Event.objects.create(
            title="Torneo Nacional de Vóley",
            description="Los mejores equipos del país compiten en Mar del Plata.",
            date=date(2025, 4, 20),
            price=3500,
            venue=estadio_polideportivo,
            id_img="1E-vVofuJyroZcFQ6gVhPuY7Wdaf4LrlS",  
            total_rating=5,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento7.categorias.add(deporte)

        evento8 = Event.objects.create(
            title="Ciclo de Cine Latinoamericano",
            description="Proyección de películas destacadas de cine independiente.",
            date=date(2025, 5, 18),
            price=1500,
            venue=teatro_radio_city,
            id_img="17MhZGjv2U_alV6ebG83WLxLTS2aQYyjk",  
            total_rating=0,
            suma_puntaje=True,
            cantidad_puntos=0,
            cancelado=False
        )
        evento8.categorias.add(pelicula)

        # --- ARTE ---
        evento9 = Event.objects.create(
            title="Exposición de Arte Moderno",
            description="Obras de artistas contemporáneos locales e internacionales.",
            date=date(2025, 7, 10),
            price=2500,
            venue=centro_cultural_recoleta,
            id_img="1PDtrzf6iatUQW3d448tUutF1hgecjVJ1",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento9.categorias.add(arte)

        evento10 = Event.objects.create(
            title="Galería Nocturna",
            description="Una experiencia artística inmersiva con luces y sonidos.",
            date=date(2025, 8, 18),
            price=3000,
            venue=konex,
            id_img="1OnPnNDlCCzEv5igFqWfm-d3y7aILWseT",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento10.categorias.add(arte)

        evento11 = Event.objects.create(
            title="Arte y Naturaleza",
            description="Intervenciones artísticas en espacios verdes urbanos.",
            date=date(2025, 9, 5),
            price=2000,
            venue=teatro_gran_rix,
            id_img="1fAXy2VgGTGWjLOwYKiKP8yN_S-jgVQyt",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento11.categorias.add(arte)

        # --- MÚSICA ---
        evento12 = Event.objects.create(
            title="Festival Rock Nacional",
            description="Bandas emblemáticas del rock argentino en vivo.",
            date=date(2025, 9, 20),
            price=6000,
            venue=estadio_velez,
            id_img="1or4kgTfjTPGslApWFgug6VNK3sDbRX4d",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento12.categorias.add(musica)

        evento13 = Event.objects.create(
            title="Jazz en el Parque",
            description="Tardes de jazz al aire libre con artistas internacionales.",
            date=date(2025, 11, 5),
            price=3500,
            venue=niceto_club,
            id_img="1uMC2mS8g4V6hxOqHzBpOKmBxP8mGzaGe",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento13.categorias.add(musica)

        evento14 = Event.objects.create(
            title="Orquesta Filarmónica en Concierto",
            description="Concierto de música clásica en el Teatro Colón.",
            date=date(2025, 12, 1),
            price=4500,
            venue=teatro_colon,
            id_img="1bihHzC1USW8qMQo-hzO-nI4C6dJi_k9i",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento14.categorias.add(musica)

        # --- CONFERENCIA ---
        evento15 = Event.objects.create(
            title="Charla sobre Inteligencia Artificial",
            description="Conferencia sobre el impacto de la IA en la sociedad.",
            date=date(2025, 9, 1),
            price=4000,
            venue=movistar_arena,
            id_img="1-N4UiGcoyA-Mn3K6Ha-IOsdnYUoBoKgR",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento15.categorias.add(conferencia)

        evento16 = Event.objects.create(
            title="Economía Circular y Sustentabilidad",
            description="Expertos analizan el futuro del desarrollo sostenible.",
            date=date(2025, 10, 10),
            price=2500,
            venue=quality_espacio,
            id_img="1UJoHICZgsecRwqXoo4OYIOlRYbBBCANi",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento16.categorias.add(conferencia)

        evento17 = Event.objects.create(
            title="Congreso Internacional de Educación",
            description="Educadores de todo el mundo debaten metodologías innovadoras.",
            date=date(2025, 12, 15),
            price=5000,
            venue=teatro_real,
            id_img="13UerjUFEX8LOsIeW1PyaxJJR_VAXJ5H1",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento17.categorias.add(conferencia)

        # --- PELÍCULA ---
        evento18 = Event.objects.create(
            title="Ciclo de Cine Italiano",
            description="Proyecciones de clásicos del cine italiano con debate posterior.",
            date=date(2025, 6, 25),
            price=1000,
            venue=teatro_el_circulo,
            id_img="19hohVUqx6A0o5EkS-nPPK6hfrJklZF86",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento18.categorias.add(pelicula)

        evento19 = Event.objects.create(
            title="Estreno: El Viaje Infinito",
            description="Una nueva película de ciencia ficción argentina.",
            date=date(2025, 7, 5),
            price=1800,
            venue=arena_maipu,
            id_img="16XRVARjlzjCll9YrzROjLyE5K-YlOHEM",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento19.categorias.add(pelicula)

        evento20 = Event.objects.create(
            title="La sirenita",
            description="Selección de cortos premiados a nivel internacional.",
            date=date(2025, 8, 15),
            price=2000,
            venue=teatro_radio_city,
            id_img="1SpFaTFtyKQ2-aZHKtckIXsbegqbtsHrL",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento20.categorias.add(pelicula)

        # --- TEATRO ---
        evento21 = Event.objects.create(
            title="Obra: La Casa de Bernarda Alba",
            description="Clásico de Lorca con una puesta moderna.",
            date=date(2025, 9, 12),
            price=3500,
            venue=teatro_independencia,
            id_img="1ReKIYQfDk1rv468sazQg1y5ADyT4K1mA",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento21.categorias.add(teatro)

        evento22 = Event.objects.create(
            title="Teatro Improvisado",
            description="Una noche sin guión donde el público decide todo.",
            date=date(2025, 10, 8),
            price=3000,
            venue=teatro_gran_rix,
            id_img="12D75wQrx06dq1xgn-NMct_y5w7ZSVW2T",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento22.categorias.add(teatro)

        evento23 = Event.objects.create(
            title="Comedia Musical: Tango y Pasión",
            description="Bailarines y actores en una historia de amor y tango.",
            date=date(2025, 11, 20),
            price=5500,
            venue=teatro_radio_city,
            id_img="1PJAKiCal9MP0PbpGFKjGTB4x1fescAum",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento23.categorias.add(teatro)

        # --- DEPORTE ---
        evento24 = Event.objects.create(
            title="Partido de Fútbol - Superclásico",
            description="El clásico del fútbol argentino en el Monumental.",
            date=date(2025, 9, 30),
            price=8000,
            venue=estadio_velez,
            id_img="1j_yTN7Kf_ZRg_qE6p6KkLgdaOJE9M1nB",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento24.categorias.add(deporte)

        evento25 = Event.objects.create(
            title="Carrera 10K Ciudad de Buenos Aires",
            description="Competencia urbana abierta al público.",
            date=date(2025, 10, 22),
            price=1000,
            venue=estadio_polideportivo,
            id_img="1Glks7SnbmPKZiMI_rB8_5zvfC2Ifx0SP",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento25.categorias.add(deporte)

        evento26 = Event.objects.create(
            title="Torneo de Tenis Abierto",
            description="Los mejores tenistas del país compiten en el Lawn Tennis.",
            date=date(2025, 11, 2),
            price=3500,
            venue=metropolitano_rosario,
            id_img="1kRMUrGZFth2DzisOrMr0RpKWuz6Hagi9",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento26.categorias.add(deporte)

        # --- TECNOLOGÍA ---
        evento27 = Event.objects.create(
            title="Expo Tecnología 2025",
            description="Últimos avances en robótica, IA y realidad aumentada.",
            date=date(2025, 7, 1),
            price=4500,
            venue=quality_espacio,
            id_img="1zEXloj460EPhOQhnpWRGQYojn18beRwG",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento27.categorias.add(tecnologia)

        evento28 = Event.objects.create(
            title="Hackatón de Innovación",
            description="Equipos compiten para desarrollar la mejor solución tecnológica.",
            date=date(2025, 9, 10),
            price=0,
            venue=teatro_real,
            id_img="1KNNZXrxRsQAf0XJ1l73StB8DtVGZxQlz",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento28.categorias.add(tecnologia)

        evento29 = Event.objects.create(
            title="Conferencia Blockchain",
            description="Especialistas explican cómo transformar procesos con blockchain.",
            date=date(2025, 8, 20),
            price=4000,
            venue=movistar_arena,
            id_img="18YGM8jdvnOcAdYqtHklXkmGNlw0BwHi-",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento29.categorias.add(tecnologia)


        evento30 = Event.objects.create(
            title="Noche de Poesía y Café",
            description="Lectura de poesía contemporánea en un ambiente íntimo.",
            date=date(2025, 6, 30),
            price=800,
            venue=niceto_club,
            id_img="1b1RG7WCyKHCF-8MzCyK8KBUE_XyIe73v",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento30.categorias.add(literatura)
        
        evento31 = Event.objects.create(
            title="Encuentro de Narradores Urbanos",
            description="Cuentistas contemporáneos relatan historias inspiradas en la ciudad.",
            date=date(2025, 7, 7),
            price=1000,
            venue=centro_cultural_recoleta,
            id_img="1gDydPPrPt0YiJM8ekGzNO3TTHbBiFnrM",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento31.categorias.add(literatura)

        evento32 = Event.objects.create(
            title="Literatura y Rock Nacional",
            description="Un cruce entre textos clásicos y música en vivo.",
            date=date(2025, 7, 14),
            price=1200,
            venue=konex,
            id_img="1RDab8UiNywFr5SZwrM0wPeB_jIBG-Wal",
            total_rating=0,
            suma_puntaje=False,
            cantidad_puntos=0,
            cancelado=False
        )
        evento32.categorias.add(literatura)

                

        # Crear tickets comprados por clientes
        ticket1 = Ticket.objects.create(
            user=cliente1,
            event=evento1,
            quantity=3,
            total=15000,
            ticket_code=str(uuid.uuid4())
        )
        
        ticket2 = Ticket.objects.create(
            user=cliente1,
            event=evento4,
            quantity=2,
            total=10000,
            ticket_code=str(uuid.uuid4())
        )
        ticket3 = Ticket.objects.create(
            user=cliente1,
            event=evento5,
            quantity=1,
            total=5000,
            ticket_code=str(uuid.uuid4())
        )
        ticket4 = Ticket.objects.create(
            user=cliente2,
            event=evento4,
            quantity=2,
            total=5000,
            ticket_code=str(uuid.uuid4())
        )
        ticket5 = Ticket.objects.create(
            user=cliente2,
            event=evento5,
            quantity=2,
            total=10000,
            ticket_code=str(uuid.uuid4())
        )
        ticket6 = Ticket.objects.create(
            user=cliente3,
            event=evento6,
            quantity=1,
            total=2000,
            ticket_code=str(uuid.uuid4())
        )
        ticket7 = Ticket.objects.create(
            user=cliente1,
            event=evento7,
            quantity=4,
            total=14000,
            ticket_code=str(uuid.uuid4())
        )
        ticket8 = Ticket.objects.create(
            user=cliente2,
            event=evento8,
            quantity=2,
            total=3000,
            ticket_code=str(uuid.uuid4())
        )

        ticket9 = Ticket.objects.create(
            user=cliente3,
            event=evento8,
            quantity=1,
            total=1000,
            ticket_code=str(uuid.uuid4())
        )

        # Crear calificaciones
        Rating.objects.create(
            title='Inolvidable',
            user=cliente1,
            event=evento7,
            rating=5,
            text="Un placer ver al mejor equipo del país en acción"
        )
        Rating.objects.create(
            title='Chico',
            user=cliente2,
            event=evento6,
            rating=3,
            text="Mucha gente"
        )


        #Comentarios
        Comment.objects.create(
            title=str(evento4.title),
            event=evento4,
            text='¿Quién más va?',
            user=cliente2,
            created_at=date(2025, 6, 1),
        )

        Comment.objects.create(
            title=str(evento2.title),
            event=evento2,
            text='¿Cuándo es?',
            user=cliente2,
            created_at=date(2025, 6, 10),
        )

        Comment.objects.create(
            title=str(evento3.title),
            event=evento3,
            text='Puedo esperar',
            user=cliente2,
            created_at=date(2025, 6, 14),
        )

        Comment.objects.create(
            title=str(evento1.title),
            event=evento1,
            text="No puedo esperar",
            user=cliente1,
            created_at=date(2025, 6, 12),
        )

        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales cargados correctamente.'))