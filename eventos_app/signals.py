from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import (
    CustomUser,
    Category,
    Venue,
    Event,
    RefundRequest,
    Comment,
    Ticket,
    Rating,
    Favorito,
    Notification,
)

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
    content_type_rating = ContentType.objects.get_for_model(Rating)
    content_type_favorito = ContentType.objects.get_for_model(Favorito) 
    content_type_venue = ContentType.objects.get_for_model(Venue)
    content_type_category = ContentType.objects.get_for_model(Category)
    content_type_ticket = ContentType.objects.get_for_model(Ticket)
    content_type_user = ContentType.objects.get_for_model(CustomUser)

    
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
    add_ratting = Permission.objects.get(codename='add_rating_rating', content_type=content_type_rating)
    change_ratting = Permission.objects.get(codename='change_rating_rating', content_type=content_type_rating)
    delete_ratting = Permission.objects.get(codename='delete_rating_rating', content_type=content_type_rating)

    # Permisos para Tickets: crear, editar, eliminar   
    add_tickets = Permission.objects.get(codename='add_ticket', content_type=content_type_ticket)
    change_tickets = Permission.objects.get(codename='change_ticket', content_type=content_type_ticket)
    delete_tickets = Permission.objects.get(codename='delete_ticket', content_type=content_type_ticket)

    # Permisos para Favoritos: agregar, eliminar
    add_favorito = Permission.objects.get(codename='add_favorito', content_type=content_type_favorito)
    delete_favorito = Permission.objects.get(codename='delete_favorito', content_type=content_type_favorito)

    # Permisos para Venue: crear, editar, eliminar
    add_venue = Permission.objects.get(codename='add_venue', content_type=content_type_venue)
    change_venue = Permission.objects.get(codename='change_venue', content_type=content_type_venue)
    delete_venue = Permission.objects.get(codename='delete_venue', content_type=content_type_venue)

    # Permisos para Category: crear, editar, eliminar
    add_category = Permission.objects.get(codename='add_category', content_type=content_type_category)
    change_category = Permission.objects.get(codename='change_category', content_type=content_type_category)
    delete_category = Permission.objects.get(codename='delete_category', content_type=content_type_category)

    # Permisos para User: crear, editar, eliminar
    add_user = Permission.objects.get(codename='add_customuser', content_type=content_type_user)
    change_user = Permission.objects.get(codename='change_customuser', content_type=content_type_user)
    delete_user = Permission.objects.get(codename='delete_customuser', content_type=content_type_user)
    view_user = Permission.objects.get(codename='view_customuser', content_type=content_type_user)

    # Ahora asignamos los persmisos según rol
    if instance.rol == 'VENDEDOR':
        instance.user_permissions.add(
            view_evento, change_evento,
            change_comentario, delete_comentario, 
            change_reembolso, accept_reembolso, reject_reembolso,
            add_notif, change_notif, delete_notif,     
            add_ratting, change_ratting,
            change_tickets, delete_tickets,      
        )
    
    elif instance.rol == 'CLIENTE':
        instance.user_permissions.add(
            view_evento,
            add_comentario, change_comentario, delete_comentario,
            add_reembolso, read_notif,
            add_ratting, change_ratting, delete_ratting,
            add_favorito, delete_favorito,
        )

    elif instance.rol == 'ADMIN':
            instance.is_staff = True
            instance.is_superuser = True
            instance.save()
'''
receiver(post_migrate)
def cargar_datos_iniciales(sender, **kwargs):
    try:
        call_command('pueblaDatos')
        print("✅ Datos iniciales cargados correctamente (desde signals).")
    except Exception as e:
        print(f"⚠️ Error cargando datos iniciales desde signals: {e}")
'''