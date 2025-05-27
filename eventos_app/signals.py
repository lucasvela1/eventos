from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser
from eventos.models import Category, Venue, Event, RefundRequest, Comment, Ticket, Rating, Favorito, Notification   # Importá los modelos sobre los que van los permisos

"""
Definís los permisos de acceso. Acá es donde decís:
Qué puede hacer cada usuario, según su rol (CLIENTE, VENDEDOR, ADMIN).
Esto lo hacés con los permisos estándar de Django: view, add, change, delete para cada modelo.
"""

@receiver(post_save, sender=CustomUser)
def assign_user_permissions(sender, instance, created, **kwargs):
    if not created:
        return
    
    # Definición de permisos comunes una sola vez
    content_type_evento = ContentType.objects.get_for_model(Event)
    content_type_comentario = ContentType.objects.get_for_model(Comment)
    content_type_reembolso = ContentType.objects.get_for_model(RefundRequest)
    content_type_notificacion = ContentType.objects.get_for_model(Notification)
    # Agregar otros content_types para otros modelos
    
    # Permisos para Evento
    view_evento = Permission.objects.get(codename='view_evento', content_type=content_type_evento)
    change_evento = Permission.objects.get(codename='change_evento', content_type=content_type_evento)
    
    # Permisos para Comentario
    add_comentario = Permission.objects.get(codename='add_comentario', content_type=content_type_comentario)
    change_comentario = Permission.objects.get(codename='change_comentario', content_type=content_type_comentario)
    delete_comentario = Permission.objects.get(codename='delete_comentario', content_type=content_type_comentario)

    # Permisos para Reembolso: crear, editar, aceptar o rechazar reembolso
    add_reembolso = Permission.objects.get(codename='add_refundrequest', content_type=content_type_reembolso)
    change_reembolso = Permission.objects.get(codename='change_refundrequest', content_type=content_type_reembolso)
    accept_reembolso = Permission.objects.get(codename='accept_refundrequest', content_type=content_type_reembolso)
    reject_reembolso = Permission.objects.get(codename='reject_refundrequest', content_type=content_type_reembolso)

    # Permisos para Notificacion: crear, editar, eliminar  y marcar como leida 
    add_notif = Permission.objects.get(codename='add_notification', content_type=content_type_notificacion)
    change_notif = Permission.objects.get(codename='change_notification', content_type=content_type_notificacion)
    delete_notif = Permission.objects.get(codename='delete_notification', content_type=content_type_notificacion)
    read_notif = Permission.objects.get(codename='read_notification', content_type=content_type_notificacion)

    # Permisos para Rating: calificar, editar y eliminar una calificacion a un evento

    # Permisos para Tickets: crear, editar, eliminar   

    # Ahora asignamos según rol
    if instance.rol == 'VENDEDOR':
        instance.user_permissions.add(
            view_evento, change_evento,
            change_comentario, delete_comentario, 
            change_reembolso, accept_reembolso, reject_reembolso,
            add_notif, change_notif, delete_notif,     
            #AGREGAR PERMISOS FALTANTES       
        )
    
    elif instance.rol == 'CLIENTE':
        instance.user_permissions.add(
            view_evento,
            add_comentario, change_comentario, delete_comentario,
            add_reembolso, read_notif,
        )

    elif instance.rol == 'ADMIN':
            instance.is_staff = True
            instance.is_superuser = True
            instance.save()