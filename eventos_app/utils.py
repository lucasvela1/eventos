from .models import Event
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from django.db.models import Case, When, Value, IntegerField, Avg, Count, Sum

"""6 Eventos ordenados por tickets comprados, cantidad de favoritos y nombre. Sin contar cancelados o que paso su fecha"""
def obtener_eventos_destacados(limit=6):
    # Fecha actual para filtrar eventos que ya pasaron
    today = now().date()
    return Event.objects.filter(
        # 1. Sin contar cancelados
        cancelado=False,
        # 2. O que no haya pasado su fecha (incluye eventos de hoy)
        date__gte=today
    ).annotate(
        # 3. Contar la cantidad de favoritos 
        num_favoritos=Count('favoritos_evento', distinct=True),
        # 4. Sumar la cantidad de tickets comprados a través del modelo Ticket
        # Usamos Coalesce para que los eventos sin tickets tengan un valor de 0 en lugar de None
        total_tickets_vendidos=Coalesce(Sum('ticket__quantity'), 0, output_field=IntegerField())
    ).order_by(
        '-total_tickets_vendidos',
        '-num_favoritos',
        'title'  
    )[:limit]

"""10 Eventos ordenados por fecha, sin incluir los cancelados"""
def obtener_eventos_proximos(limit=10):
    return Event.objects.filter(
        cancelado=False, 
        date__gte=timezone.now()
        ).order_by('date')[:limit]


def actualizar_total_rating(event):
    
    # Se obtienen todos los ratings asociados al evento y se calcula el promedio
    avg_dict = event.rating_set.aggregate(promedio=Avg('rating'))
    
    # El resultado es un diccionario Extraemos el valor.
    avg_rating = avg_dict.get('promedio')

    # Si hay ratings, se redondea. Si no hay (es None), se deja en 0.
    if avg_rating is not None:
        event.total_rating = round(avg_rating)
    else:
        event.total_rating = 0
    
    event.save(update_fields=['total_rating'])