from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import (
    Event, Comment, CustomUser, UserRole, Category, Venue,
    RefundRequest, Ticket, Rating, Favorito, Notification
)

# Administración del modelo Event
admin.site.site_header = "Panel de Administración - Grupo 4"
admin.site.site_title = "Administración de Eventos"
admin.site.index_title = "Bienvenido al panel de administración"

class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date','venue','price','cancelado']
    list_editable = ['price', 'date', 'cancelado']
    search_fields =['title', 'description']
    list_filter = ['categoria', 'venue', 'cancelado']
    list_per_page = 10
    ordering = ['-date']

    actions = ['cancelar_eventos', 'habilitar_eventos','duplicar_eventos'] #Donde metermos las acciones personalizadas del evento
    
    def duplicar_eventos(self,request, queryset):
        for event in queryset: #Por cada evento seleccionad le creamos una copia, para que sea más comodo la creacion de un nuevo evento
            nuevo_evento = Event.objects.create(
                title = f"{event.title} (Copia)",
                description = event.description,
                date = event.date,
                price = event.price,
                categoria = event.categoria,
                venue = event.venue,
                id_img = event.id_img,
                cancelado = False,
                capacidad_ocupada = 0,
            )
          
    def cancelar_eventos(self, request, queryset):
        eventos_actualizados = queryset.update(cancelado=True)

    def habilitar_eventos(self, request, queryset):
        eventos_actualizados = queryset.update(cancelado=False)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if request.user.rol == 'VENDEDOR':
            return ['created_at', 'updated_at', 'total_rating', 'cantidad_puntos', 'suma_puntaje']
        return super().get_readonly_fields(request, obj)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.rol == 'VENDEDOR':
            return qs
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.rol == 'VENDEDOR':
            return True
        return False
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if hasattr(request.user, 'rol') and request.user.rol == 'VENDEDOR':
            return {'cancelar_eventos': actions['cancelar_eventos'], 'habilitar_eventos': actions['habilitar_eventos']}
        
        return actions

# Administración del modelo Comment
class CommentAdmin(admin.ModelAdmin):
    list_display = ['title','user', 'created_at']
    ordering = ['-created_at']    

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if request.user.rol == 'VENDEDOR':
            return ['created_at', 'user', 'event']
        return super().get_readonly_fields(request, obj)


# Administración del modelo CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_superuser', 'puntaje']
    actions = ['reiniciar_puntaje']
    ordering = ['-is_superuser','-puntaje']

    fieldsets = list(UserAdmin.fieldsets) + [
        ('Información Adicional', {'fields': ('rol', 'puntaje')}),
    ]
    add_fieldsets = list(UserAdmin.add_fieldsets) + [
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'rol', 'password1', 'password2'),
        }),
    ]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'rol') and request.user.rol == UserRole.VENDEDOR:
            if hasattr(request.user, 'id'):
                return qs.filter(id=request.user.id)
        return qs.none()
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if hasattr(request.user, 'rol') and request.user.rol == UserRole.VENDEDOR:
            return ['username', 'email', 'rol']
        return super().get_readonly_fields(request, obj)
        return super().get_readonly_fields(request, obj)
    
    def reiniciar_puntaje(self, request, queryset):
        for user in queryset:
            user.puntaje = 0
            user.save()
        self.message_user(request, "Puntajes reiniciados exitosamente.")
    
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'address','city','capacity','contact']
    #list_editable = ['address']
    search_fields =['name']
    list_filter = ['name']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'read']
    search_fields = ['title', 'user']
    ordering = ['read','-created_at']    
    actions = ['marcar_como_leida', 'marcar_como_no_leida']
    
    def marcar_como_leida(self, request, queryset):
        queryset.update(read=True)
        self.message_user(request, "Notificaciones marcadas como leídas.")

    def marcar_como_no_leida(self, request, queryset):
        queryset.update(read=False)
        self.message_user(request, "Notificaciones marcadas como no leídas.")    

    def has_module_permission(self, request):
        return request.user.is_superuser



class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'ticket_code', 'reason', 'approved', 'created_at']
    search_fields = ['user__username', 'reason', 'ticket_code']
    list_filter = ['approved', 'created_at']
    ordering = ['approved', '-created_at']
    actions = ['aprobar_solicitud', 'rechazar_solicitud']

    def aprobar_solicitud(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Las solicitudes seleccionadas han sido aprobadas.")

    def rechazar_solicitud(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, "Las solicitudes seleccionadas han sido rechazadas.")


    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        
        if hasattr(request.user, 'rol') and request.user.rol == 'VENDEDOR':
            if obj:
                return [field.name for field in self.model._meta.fields]
        
        return super().get_readonly_fields(request, obj)

    def aprobar_solicitud(self, request, queryset):
        for refund in queryset:
            refund.approved = True
            refund.save()
            self.message_user(request, f"Solicitud de reembolso aprobada para {refund.user.username}.")

    def rechazar_solicitud(self, request, queryset):
        for refund in queryset:
            refund.approved = False
            refund.save()
            self.message_user(request, f"Solicitud de reembolso rechazada para {refund.user.username}.")      

class TicketAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'quantity', 'total', 'buy_date', 'ticket_code']
    search_fields = ['event__title', 'user__username']
    list_filter = ['event', 'buy_date']
    ordering = ['-buy_date']

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        
        if hasattr(request.user, 'rol') and request.user.rol == 'VENDEDOR':
            if obj:
                return [field.name for field in self.model._meta.fields]
        
        return super().get_readonly_fields(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','description','is_active']
    search_fields =['description']
    ordering =['name']


class RatingAdmin(admin.ModelAdmin):
    list_display = ['title','user','created_at', 'rating']
    search_fields = ['user','text']
    list_filter = ['rating']
    ordering = ['-rating']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        
        if hasattr(request.user, 'rol') and request.user.rol == 'VENDEDOR':
            if obj:
                return [field.name for field in self.model._meta.fields]
        
        return super().get_readonly_fields(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

# Registrar los modelos
admin.site.register(Event, EventAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(RefundRequest, RefundRequestAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Favorito)
admin.site.register(Notification, NotificationAdmin)

