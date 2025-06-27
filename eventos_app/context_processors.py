from .models import Notification

def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        total_unread = Notification.objects.filter(user=request.user, read=False).count()
        return {'total_unread': total_unread}
    return {'total_unread': 0}
