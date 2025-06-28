from django.db import models
from django.contrib.auth.models import AbstractUser #para heredar el usuario definido en Django
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.core.exceptions import ValidationError
from .managers import NotificationManager, EventManager, RatingManager


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    id_img = models.CharField(max_length=2083, default='sin_imagen')

    def __str__(self):
        return self.name
    
    def clean(self):
        super().clean()
        if ((not self.name)|(self.name.strip() == "")):
            raise ValidationError({'name': 'El nombre de la categoría es requerido.'})

        if ((not self.description)|(self.description.strip() == "")):
            raise ValidationError({'description': 'La descripción de la categoría es requerida.'})
    
    def imagen_url_directa(self):
        return f'https://drive.google.com/thumbnail?id={self.id_img}'



class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.TextField()
    capacity = models.PositiveIntegerField(default=100)
    contact =models.TextField()

    def clean(self):
        super().clean()
        if self.capacity < 1:
            raise ValidationError({'capacity': 'La capacidad no puede ser negativa o cero.'})
        
        if ((not self.name)|(self.name.strip() == "")):
            raise ValidationError({'name': 'El nombre del lugar es requerido.'})

        if ((not self.address)|(self.address.strip() == "")):
            raise ValidationError({'address': 'La dirección del lugar es requerida.'})

        if ((not self.city)|(self.city.strip() == "")):
            raise ValidationError({'city': 'La ciudad del lugar es requerida.'})
        if ((not self.contact)|(self.contact.strip() == "")):
            raise ValidationError({'contact': 'El contacto del lugar es requerido.'})        

    def __str__(self):
        return self.name
    
class Event(models.Model):
    objects = EventManager()
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    price=models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_rating = models.PositiveIntegerField(default=0)
    categorias = models.ManyToManyField(Category, blank=True, related_name='events')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=False)
    suma_puntaje=models.BooleanField(default=False)
    cantidad_puntos=models.PositiveIntegerField(default=0)
    cancelado=models.BooleanField(default=False)
    id_img = models.CharField(max_length=2083, default='sin_imagen') # Solamente id de la imagen
    capacidad_ocupada=models.PositiveIntegerField(default=0)
    
    def clean(self):
        super().clean()
        if self.date < now().date():
            raise ValidationError({'date': 'La fecha del evento no puede ser una fecha pasada.'})

        if self.venue and self.capacidad_ocupada > self.venue.capacity:
            raise ValidationError(
                {'capacidad_ocupada': f'La capacidad ocupada ({self.capacidad_ocupada}) no puede exceder la capacidad del lugar, que es {self.venue.capacity}.'}
            )
        
        if ((not self.title)|(self.title.strip() == "")):
            raise ValidationError({'title': 'El título del evento no puede estar vacío.'})
        
        if self.description == "":
            raise ValidationError({'description': 'La descripción del evento no puede estar vacía.'})

    def __str__(self):
        return self.title
       
    def imagen_url_directa(self):
        return f'https://drive.google.com/thumbnail?id={self.id_img}'
    
    @property
    def finalizado(self):
        return self.date < now().date()- timedelta(days=1)


class Priority(models.TextChoices):
    high = 'HIGH'
    medium = 'MEDIUM'
    low = 'LOW'


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    VENDEDOR = 'VENDEDOR', 'Vendedor'
    CLIENTE = 'CLIENTE', 'Cliente'


class CustomUser(AbstractUser):
    puntaje= models.PositiveIntegerField(default=0)
    rol = models.CharField(
        max_length=10, 
        choices=UserRole.choices, 
        default=UserRole.CLIENTE     #Solo se puede elegir entre los roles ya creados
        ) 
    email = models.EmailField(unique=True, blank=False, null=False)                                         

    def __str__(self):
        return self.username
    
    def clean(self):
        super().clean()
        if self.puntaje < 0:
            raise ValidationError({'puntaje': 'El puntaje no puede ser negativo.'})
        
        if ((not self.username)|(self.username.strip() == "")):
            raise ValidationError({'username': 'El nombre de usuario es requerido.'})

        if ((not self.email)|(self.email.strip() == "")):
            raise ValidationError({'email': 'El correo electrónico es requerido.'})
          

class Notification(models.Model):
    objects = NotificationManager()  # Añadimos el manager personalizado
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  #Se pone como DateTimeFiel para también tener la hora
    priority = models.TextField(choices=Priority.choices)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False, related_name="notifications_user")

    def __str__(self):
        return self.title
    
    
class RefundRequest(models.Model):
    approved = models.BooleanField()
    approval_date = models.DateField(null=True, blank=True) #Anteriormente tomaba la fecha de creacion como fecha de aprobacion
    ticket_code = models.TextField(unique=True)
    reason = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False )

    def __str__(self):
        return self.ticket_code
    
    class Meta:
        permissions = [
            ('can_accept_refund', 'Puede aceptar reembolsos'),
            ('can_reject_refund', 'Puede rechazar reembolsos'),
        ]
    

class Type(models.TextChoices):
    general = 'GENERAL'
    vip = 'VIP'
    

class Ticket(models.Model):
    buy_date = models.DateField(auto_now_add=True)
    ticket_code = models.TextField(unique=True)
    quantity = models.IntegerField() #Se puede hacer una compra, y en ella se pueden comprar varias entradas
    type = models.TextField(choices=Type.choices, default=Type.general)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
    total = models.IntegerField(default=0)
    
    def __str__(self):
        return self.ticket_code
    
    
class Rating(models.Model):
    objects = RatingManager()  # <--- Aquí lo usás

    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ("user", "event")
        

class Comment(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False )  
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False ) 

class Favorito(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False, related_name="favoritos_usuario")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False, related_name="favoritos_evento")
    #related_name define cómo se accede desde el otro modelo hacia este. 

    class Meta():
        unique_together = ("user", "event")

class Pago(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False)
    nombre_titular = models.CharField("Nombre del titular", max_length=100)
    numero_tarjeta = models.CharField("Número de tarjeta", max_length=16)
    fecha_vencimiento = models.CharField("Fecha de expiración (MM/AA)", max_length=5)
    cvv = models.CharField("Código de seguridad (CVV)", max_length=4)
    monto = models.DecimalField("Monto total", max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField("Fecha del pago", auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.user.username} por ${self.monto}"
    
    # Utilizaremos el algoritmo de Luhn para verificar la tarjeta
    def validar_tarjeta_luhn(numero_tarjeta: str) -> bool:
        numero_tarjeta = numero_tarjeta.replace(' ', '').replace('-', '')
        if not numero_tarjeta.isdigit():
            return False
        
        suma = 0
        alt = False

        for digito in reversed(numero_tarjeta):
            d = int(digito)
            if alt:
                d *= 2
                if d > 9:
                    d -= 9
            suma += d
            alt = not alt

        return suma % 10 == 0