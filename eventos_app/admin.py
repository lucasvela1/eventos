from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Event, Comment, CustomUser, UserRole, Category, Venue,
    RefundRequest, Ticket, Rating, Favorito, Notification
)
from .forms import CustomUserCreationForm

# Administración del modelo Event
admin.site.site_header = "Panel de Administración - Grupo 4"
admin.site.site_title = "Administración de Eventos"
admin.site.index_title = "Bienvenido al panel de administración"

class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date','venue','price','cancelado']
    list_editable = ['price']
    search_fields =['title', 'description']
    list_filter = ['categoria', 'venue', 'cancelado']
    list_per_page = 10
    ordering = ['-date']
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
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_superuser']

    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'puntaje')}),
    )

    # Agregamos esta sección para que aparezca 'rol' al crear usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'rol', 'password1', 'password2'),
        }),
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
            return ['username', 'email', 'rol']
        return super().get_readonly_fields(request, obj)
    
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'address','city','capacity','contact']
    #list_editable = ['address']
    search_fields =['name']
    list_filter = ['name']

    

# Registrar los modelos
admin.site.register(Event, EventAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Venue, VenueAdmin)
admin.site.register(RefundRequest)
admin.site.register(Ticket)
admin.site.register(Rating)
admin.site.register(Favorito)
admin.site.register(Notification)

