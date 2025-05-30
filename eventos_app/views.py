from django.views.generic import TemplateView, ListView, DetailView
from .models import Event, Notification, RefundRequest
from django.db.models import Case, When, Value, IntegerField


class HomeView(TemplateView):
    template_name = "home.html"


class EventListView(ListView):
    model = Event #Clase que manipula la vista
    template_name = "app/events.html" #Incluyo el template que controla la vista
    context_object_name = "events"

    def get_queryset(self): #Pasarle una lista distinta al context
        return Event.objects.all().order_by("date")  #Me ordena los eventos por fecha

    def get_context_data(self, **kwargs):  #Llamo al context data del padre, me traigo todos los objetos de event
        context = super().get_context_data(**kwargs)
        return context  


class EventDetailView(DetailView):
    model = Event
    template_name = "app/event_detail.html"
    context_object_name = "event"

class NotificationListView(ListView):
    model = Notification
    template_name = "app/notification.html"
    context_object_name = "notifications"

    def get_queryset(self):
        priority_order = Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            default=Value(4), # Para cualquier otro valor o si es None
            output_field=IntegerField(),
        )
        return Notification.objects.all().order_by(priority_order, "-created_at")  # Ordena las notificaciones por prioridad y luego por fecha de creación, de más reciente a más antiguo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class RefundRequestListView(ListView):
    model = RefundRequest
    template_name = "app/refundRequest.html"
    context_object_name = "refundRequests"

    def get_queryset(self):
        priority_order = Case(
            When(approved=False, then=Value(1)),
            When(approved=True, then=Value(2)),
            output_field=IntegerField(),
        )
        return RefundRequest.objects.all().order_by(priority_order, "created_at")  # Ordena las notificaciones por prioridad y luego por fecha de creación, de más reciente a más antiguo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context