from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Event, CustomUser

# Administración del modelo Event
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "date")
    search_fields = ("title", "date")
    list_filter = ("date",)


admin.site.register(Event, EventAdmin)

# Administración del modelo CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'puntaje', 'notification')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
