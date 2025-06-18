from django.db import models
from django.contrib.auth.models import AbstractUser #para heredar el usuario definido en Django
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.core.exceptions import ValidationError

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
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    price=models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_rating = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
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
    rol = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.CLIENTE) #Solo se puede elegir entre los roles ya creados

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
    approval_date = models.DateField(auto_now_add=True)
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
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=False )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False ) 

    def __str__(self):
        return self.title
    
    class Meta():
        unique_together = ("user", "event")

#calcular el puntaje de un evento.
@receiver([post_save, post_delete], sender=Rating)
def update_event_rating(sender, instance, **kwargs):
    event = instance.event
    avg = event.ratings.aggregate(avg=Avg('rating'))['avg']
    if avg:
        event.total_rating = max(0, min(5, round(avg)))  # redondeado entre 0 y 5
    else:
        event.total_rating = 0  # sin calificación
        event.save()

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