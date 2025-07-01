import django.db.models as models
from django.utils.timezone import now
from django.db.models import Case, When, Value, IntegerField, Avg, Prefetch


class NotificationManager(models.Manager):
    def unread_notifications(self, user, limit=None):
        """ Obtiene notificaciones no leídas, con un límite opcional. """
        queryset = self.filter(user=user, read=False).order_by('-created_at')
        if limit:
            return queryset[:limit]
        return queryset

    def unread_count(self, user):
        """ Devuelve la cantidad de notificaciones no leídas. """
        return self.filter(user=user, read=False).count()

    def for_user_ordered_by_priority(self, user):
        """ Obtiene todas las notificaciones de un usuario, ordenadas por prioridad y fecha. """
        priority_order = Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
        return self.filter(user=user).order_by(priority_order, "-created_at")
    

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
    
    def rated_by_user(self, user):
        from eventos_app.models import Rating

        """ Devuelve eventos que un usuario específico ya ha calificado. """
        if not user.is_authenticated:
            return self.none()
        user_ratings = Rating.objects.filter(user=user)
        return self.filter(rating__user=user).prefetch_related(
            Prefetch('rating_set', queryset=user_ratings, to_attr='user_rating')
        ).distinct()
    
    def to_be_rated_by_user(self, user):
        from eventos_app.models import Rating
        from eventos_app.models import Ticket
        # Devuelve eventos que un usuario compró, que ya finalizaron y que aún no ha calificado. 
        if not user.is_authenticated:
            return self.none()
            
        today = now().date()
        
        # IDs de eventos para los que el usuario tiene ticket
        events_with_ticket_ids = Ticket.objects.filter(user=user).values_list('event_id', flat=True)
        
        # IDs de eventos que el usuario ya calificó
        rated_event_ids = Rating.objects.filter(user=user).values_list('event_id', flat=True)

        return self.filter(
            id__in=events_with_ticket_ids
        ).exclude(
            id__in=rated_event_ids
        ).filter(
            models.Q(cancelado=True) | models.Q(date__lt=today)
        )

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
    

class TicketManager(models.Manager):
    def active_tickets_for_user(self, user):
        # Devuelve los tickets de un usuario para eventos activos (no finalizados ni cancelados). 
        if not user.is_authenticated:
            return self.none()
        today = now().date()
        return self.filter(user=user, event__date__gte=today, event__cancelado=False)

    def user_has_ticket_for_event(self, user, event):
        # Verifica si un usuario tiene un ticket para un evento específico. 
        if not user.is_authenticated:
            return False
        return self.filter(user=user, event=event).exists()

class CommentManager(models.Manager):
    def for_event(self, event):
        #Obtiene los comentarios para un evento, ordenados por fecha. 
        return self.filter(event=event).order_by('-created_at')    
