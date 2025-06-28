from .models import Notification


def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        total_unread = Notification.objects.filter(user=request.user, read=False).count()
        return {'total_unread': total_unread}
    return {'total_unread': 0}


# Este context processor inyecta automáticamente en todos los templates
# la variable 'total_unread', que representa la cantidad de notificaciones
# no leídas del usuario autenticado. Esto permite mostrar el número en
# la campanita del navbar sin necesidad de pasar esa información desde
# cada vista individual.

# Para que este processor funcione, debe estar registrado en settings.py,
# dentro de TEMPLATES > OPTIONS > context_processors.

# Uso en template: {{ total_unread }}
