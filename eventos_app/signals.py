from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    CustomUser, Category, Venue, Event, RefundRequest,
    Comment, Ticket, Rating, Favorito, Notification
)

@receiver(post_save, sender=CustomUser)
def assign_user_permissions(sender, instance, created, **kwargs):
    if not created:
        return
    
    print(f"Se creó un usuario nuevo con rol: {instance.rol}")  # Verificamos qué rol tiene
    
    # Permisos por modelo
    def get_perms(model):
        ct = ContentType.objects.get_for_model(model)
        
        return {
            'add': Permission.objects.get(codename=f'add_{model.__name__.lower()}', content_type=ct),
            'change': Permission.objects.get(codename=f'change_{model.__name__.lower()}', content_type=ct),
            'delete': Permission.objects.get(codename=f'delete_{model.__name__.lower()}', content_type=ct),
            'view': Permission.objects.get(codename=f'view_{model.__name__.lower()}', content_type=ct),
        }

    perms = {
        'event': get_perms(Event),
        'comment': get_perms(Comment),
        'refund': get_perms(RefundRequest),
        'notification': get_perms(Notification),
        'rating': get_perms(Rating),
        'ticket': get_perms(Ticket),
        'venue': get_perms(Venue),
        'category': get_perms(Category),
        'user': get_perms(CustomUser),
        'favorito': get_perms(Favorito),
    }

    # Permisos personalizados
    refund_ct = ContentType.objects.get_for_model(RefundRequest)
    accept_refund = Permission.objects.get(codename='can_accept_refund', content_type=refund_ct)
    reject_refund = Permission.objects.get(codename='can_reject_refund', content_type=refund_ct)
    
    # Asignación por rol
    if instance.rol == 'CLIENTE':
        instance.user_permissions.set([
            perms['event']['view'],
            perms['comment']['add'], perms['comment']['change'], perms['comment']['delete'],
            perms['refund']['add'],
            perms['notification']['view'],
            perms['rating']['add'], perms['rating']['change'], perms['rating']['delete'],
            perms['ticket']['add'],
            perms['favorito']['add'], perms['favorito']['delete'],
        ])

    elif instance.rol == 'VENDEDOR':
        instance.user_permissions.set([
            perms['event']['view'], perms['event']['change'],
            perms['comment']['change'], perms['comment']['delete'],
            perms['refund']['change'],
            perms['notification']['add'], perms['notification']['change'], perms['notification']['delete'],
            perms['rating']['add'], perms['rating']['change'],
            perms['ticket']['change'], perms['ticket']['delete'],
            perms['refund']['change'],
            accept_refund,
            reject_refund,
        ])
        instance.is_staff = True
        instance.save(update_fields=['is_staff'])

    elif instance.rol == 'ADMIN':
        instance.is_staff = True
        instance.is_superuser = True
        instance.save()
