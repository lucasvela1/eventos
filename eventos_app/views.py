from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.db.models import Case, When, Value, IntegerField, Avg
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Event, Notification, Favorito, Rating, RefundRequest


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
    

class FavoritosListView(ListView):
    model = Favorito
    template_name = "app/favoritos.html"
    context_object_name = "favoritos"
    login_url = "/accounts/login/"

    def get_queryset(self):
        user = self.request.user
        # Trae los favoritos del usuario, y anota el rating promedio del evento
        return (
            Favorito.objects
            .filter(user=user)
            .select_related("event")
            .annotate(rating_promedio=Avg("event__rating__rating")) #calcula promedio del evento
            .order_by("-rating_promedio") #ordena por rating
        )  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")  # Redirige a login si el registro es exitoso

    def form_valid(self, form):
        form.save()  # Guarda el nuevo usuario
        messages.success(self.request, "Usuario registrado correctamente. Ahora podés iniciar sesión.")
        return super().form_valid(form)


#para agregar o quitar favoritos
@login_required
def toggle_favorito(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    favorito, creado = Favorito.objects.get_or_create(user=request.user, event=event)

    if not creado:
        favorito.delete()  # Si ya existía, lo quitamos

    # Redirigí a donde estabas antes (o a event list si querés algo fijo)
    return redirect(request.META.get('HTTP_REFERER', 'event_list'))
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



class RankingView(ListView):
    model = Event
    template_name = "app/ranking.html"
    context_object_name = "events"

    def get_queryset(self):
        return (
            Event.objects
            .annotate(rating_promedio=Avg("rating__rating"))  # Calcula el promedio de ratings
            .order_by("-rating_promedio")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
