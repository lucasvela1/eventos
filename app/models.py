from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.TextField()
    capacity = models.IntegerField()
    contact =models.TextField()

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_rating = models.IntegerField()
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    venue = models.OneToOneField(Venue, on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return self.title

    @classmethod
    def validate(cls, title, description, date):
        errors = {}

        if title == "":
            errors["title"] = "Por favor ingrese un titulo"

        if description == "":
            errors["description"] = "Por favor ingrese una descripcion"

        return errors

    @classmethod
    def new(cls, title, description, date):
        errors = Event.validate(title, description, date)

        if len(errors.keys()) > 0:
            return False, errors

        Event.objects.create(
            title=title,
            description=description,
            date=date,
        )

        return True, None

    def update(self, title, description, date):
        self.title = title or self.title
        self.description = description or self.description
        self.date = date or self.date

        self.save()

class Priority(models.TextChoices):
    high = 'HIGH'
    medium = 'MEDIUM'
    low = 'LOW'

class Notification(models.Model):
    title = models.CharField(max_length=200)
    messaje = models.TextField()
    created_at = models.DateField(auto_now_add=True) 
    priority = models.TextField(choices=Priority.choices)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.TextField()
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True )

    def __str__(self):
        return self.username



class RefundRequest(models.Model):
    approved = models.BooleanField()
    approval_date = models.DateField(auto_now_add=True)
    ticket_code = models.TextField(unique=True)
    reason = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=False )

    def __str__(self):
        return self.ticket_code
    

class Type(models.TextChoices):
    general = 'GENERAL'
    vip = 'VIP'

class Ticket(models.Model):
    buy_date = models.DateField(auto_now_add=True)
    ticket_code = models.TextField(unique=True)
    quantity = models.IntegerField()
    type = models.TextField(choices=Type.choices, default=Type.general)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=False)
    event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True, blank=False) #VER SI ES CLAVE FORANEA

    def __str__(self):
        return self.ticket_code

class Rating(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=False )
    event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True, blank=False )

    def __str__(self):
        return self.ticket_title

class Comment(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=False )
    event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True, blank=False )