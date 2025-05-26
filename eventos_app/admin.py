from django.contrib import admin
from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "date")
    search_fields = ("title", "date")
    list_filter = ("date",)


admin.site.register(Event, EventAdmin)
