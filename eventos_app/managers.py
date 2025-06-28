import django.db.models as models
from django.utils.timezone import now
from django.db.models import Case, When, Value, IntegerField,Avg

class NotificationManager(models.Manager):
    def unread_notifications(self, user):
        return self.filter(user=user, read=False).order_by('-created_at')
    

class EventManager(models.Manager):

    def activos_para_usuario(self, user):
        today = now().date()
        queryset = self.get_queryset().filter(date__gte=today, cancelado=False).order_by("date")

        if user.is_authenticated:
            favoritos_ids = self.favoritos_ids_para_usuario(user)
            queryset = queryset.annotate(
                is_favorito=Case(
                    When(pk__in=favoritos_ids, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
            queryset = queryset.order_by('-is_favorito', 'date')

        return queryset

    def favoritos_ids_para_usuario(self, user):
        if user.is_authenticated:
            return user.favoritos_usuario.values_list('event_id', flat=True)
        return []

    
class VenueManager(models.Manager):

    def con_capacidad_mayor_a(self, capacidad_minima):
        return self.filter(capacity__gte=capacidad_minima)

    def en_ciudad(self, ciudad):
        return self.filter(city__iexact=ciudad.strip())

    def con_nombre_que_contenga(self, texto):
        return self.filter(name__icontains=texto.strip())
    
    
    def favoritos_ids_para_usuario(self, user):
        if user.is_authenticated:
            return list(user.favoritos_usuario.values_list('event_id', flat=True))
        return []
    

class RatingManager(models.Manager):
    def for_event(self, event):
        return self.filter(event=event)

    def average_for_event(self, event):
        result = self.filter(event=event).aggregate(avg=Avg('rating'))['avg']
        return round(result) if result else 0

    def user_has_rated(self, user, event):
        return self.filter(user=user, event=event).exists()

    def recent(self, limit=5):
        return self.order_by('-created_at')[:limit]
    
