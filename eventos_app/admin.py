from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Event, Comment, CustomUser, UserRole, Category, Venue, RefundRequest, Ticket, Rating, Favorito, Notification

"""
Este archivo controla lo que los usuarios con acceso al panel de administración pueden ver y editar. Acá podés:
Ocultar campos que no querés que se vean (get_fields).
Hacer que ciertos campos no se puedan editar (get_readonly_fields).
Filtrar objetos para que un usuario solo vea sus propios datos, por ejemplo (get_queryset).
Bloquear ciertas acciones como agregar o eliminar objetos (has_add_permission, has_delete_permission).
"""

# Administración del modelo Event
class EventAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None): #solo lectura
        if request.user.is_superuser:
            return []  # superadmin puede editar todo
        if request.user.rol == 'VENDEDOR':
            return ['created_at', 'updated_at', 'total_rating', 'cantidad_puntos', 'suma_puntaje']
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.rol == 'VENDEDOR':
            return qs.filter(vendedor=request.user)  # Suponiendo que Event tiene campo vendedor
        return qs.none()

# Administración del modelo Comment
class CommentAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if request.user.rol == 'VENDEDOR':
            return ['created_at', 'user', 'event']
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.rol == 'VENDEDOR':
            return qs.filter(user=request.user)
        return qs.none()

# Administración del modelo CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'puntaje', 'notification')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.rol == UserRole.VENDEDOR:
            return qs.filter(id=request.user.id)
        return qs.none()

    def get_readonly_fields(self, request, obj=None):  
        if request.user.is_superuser:
            return []
        if request.user.rol == UserRole.VENDEDOR:
            # Puedes hacer que no puedan editar ciertos campos aquí
            return ['username', 'email', 'rol']
        return super().get_readonly_fields(request, obj)

# Registrar otros modelos sin modificaciones especiales
admin.site.register(Event, EventAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Venue)
admin.site.register(RefundRequest)
admin.site.register(Ticket)
admin.site.register(Rating)
admin.site.register(Favorito)
admin.site.register(Notification)