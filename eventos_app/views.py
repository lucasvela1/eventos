from django.views.generic import TemplateView, ListView, DetailView
from .models import Event


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
