from .models import Event,Rating
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from django.db.models import Case, When, Value, IntegerField, Avg, Count, Sum
import math

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

# actualiza el total_rating de un evento
def actualizar_total_rating(evento):
    promedio = Rating.objects.filter(event=evento).aggregate(promedio=Avg('rating'))['promedio']
    if promedio is not None:
        evento.total_rating = round(promedio)
    else:
        evento.total_rating = 0
    evento.save(update_fields=['total_rating'])

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