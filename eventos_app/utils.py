from .models import Event
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField

"""6 Eventos ordenados por rating y luego por orden alfabetico"""
def obtener_eventos_destacados(limit=6):
    return Event.objects.filter(cancelado=False).annotate(
        tiene_rating=Case(
            When(total_rating__gt=0, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-tiene_rating', 'title')[:limit]

"""10 Eventos ordenados por fecha, sin incluir los cancelados"""
def obtener_eventos_proximos(limit=10):
    return Event.objects.filter(
        cancelado=False, 
        date__gte=timezone.now()
        ).order_by('date')[:limit]
