from django.db import models
from django.contrib.auth.models import AbstractUser #para heredar el usuario definido en Django
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    id_img = models.CharField(max_length=2083, default='sin_imagen')

    def __str__(self):
        return self.name
    
    @classmethod
    def validate(cls, name):
        errors = {}
        if not name:
            errors["name"] = "Por favor ingrese un nombre"
        return errors

    @classmethod
    def new(cls, name, description="", is_active=True, id_img="sin_imagen"):
        errors = cls.validate(name)
        if errors:
            return False, errors
        cls.objects.create(name=name, description=description, is_active=is_active, id_img=id_img)
        return True, None

    def update(self, name=None, description=None, is_active=None, id_img=None):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_active is not None:
            self.is_active = is_active
        if id_img is not None:
            self.id_img = id_img
        self.save()
    
    def imagen_url_directa(self):
        return f'https://drive.google.com/thumbnail?id={self.id_img}'


class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.TextField()
    capacity = models.IntegerField(default=100)
    contact =models.TextField()

    def __str__(self):
        return self.name
    
    @classmethod
    def validate(cls, name, address, city, capacity, contact):
        errors = {}
        if not name:
            errors["name"] = "El nombre es requerido"
        if capacity is not None and capacity < 0:
            errors["capacity"] = "La capacidad no puede ser negativa"
        return errors

    @classmethod
    def new(cls, name, address, city, capacity, contact):
        errors = cls.validate(name, address, city, capacity, contact)
        if errors:
            return False, errors
        cls.objects.create(name=name, address=address, city=city, capacity=capacity, contact=contact)
        return True, None

    def update(self, name=None, address=None, city=None, capacity=None, contact=None):
        self.name = name or self.name
        self.address = address or self.address
        self.city = city or self.city
        self.capacity = capacity if capacity is not None else self.capacity
        self.contact = contact or self.contact
        self.save()


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    price=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_rating = models.IntegerField(default=0)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=False)
    suma_puntaje=models.BooleanField(default=False)
    cantidad_puntos=models.IntegerField(default=0)
    cancelado=models.BooleanField(default=False)
    id_img = models.CharField(max_length=2083, default='sin_imagen') # Solamente id de la imagen
    capacidad_ocupada=models.IntegerField(default=0)

    def __str__(self):
        return self.title

    @classmethod
    def validate(cls, title, description, date, id_img):
        errors = {}

        if title == "":
            errors["title"] = "Por favor ingrese un titulo"

        if description == "":
            errors["description"] = "Por favor ingrese una descripcion"

        return errors

    @classmethod
    def new(cls, title, description, date, price, id_img):
        errors = Event.validate(title, description, date)

        if len(errors.keys()) > 0:
            return False, errors

        Event.objects.create(
            title=title,
            description=description,
            date=date,
            price=price,
            id_img=id_img
        )

        return True, None

    def update(self, title, description, date, id_img):
        self.save()
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if date is not None:
            self.date = date
        if id_img is not None:
            self.id_img = id_img
        self.save()     
   
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
    puntaje= models.IntegerField(default=0)
    rol = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.CLIENTE) #Solo se puede elegir entre los roles ya creados

    def __str__(self):
        return self.username
    
    @classmethod
    def validate(cls, username, email):
        errors = {}
        if not username or username.strip() == "":
            errors["username"] = "Por favor ingrese un nombre de usuario"

        if not email or email.strip() == "":
            errors["email"] = "Por favor ingrese un correo electrónico"

        return errors

    @classmethod
    def new(cls, username, email, notification=None):
        errors = cls.validate(username, email)
        if errors:
            return False, errors

        cls.objects.create(username=username, email=email, notification=notification)
        return True, None

    def update(self, username=None, email=None, notification=None):
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if notification is not None:
            self.notification = notification
        self.save()


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