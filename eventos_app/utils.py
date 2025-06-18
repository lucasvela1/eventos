from .models import Event,Rating
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField, Avg
import math

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

# actualiza el total_rating de un evento
def actualizar_total_rating(evento):
    promedio = Rating.objects.filter(event=evento).aggregate(promedio=Avg('rating'))['promedio']
    if promedio is not None:
        evento.total_rating = round(promedio)
    else:
        evento.total_rating = 0
    evento.save(update_fields=['total_rating'])