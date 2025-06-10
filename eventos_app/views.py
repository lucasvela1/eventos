from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, FormView

from .forms import RatingForm, UsuarioRegisterForm
from .models import Event, Favorito, Notification, Rating, RefundRequest, Ticket




class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.all().order_by("date")  # Pasa la lista de eventos al contexto
        return context


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
    

class FavoritosListView(LoginRequiredMixin, ListView):
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

class ToggleFavoritoView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        favorito, creado = Favorito.objects.get_or_create(user=request.user, event=event)
        if not creado:
            favorito.delete()
        return redirect(request.META.get('HTTP_REFERER', 'favoritos'))
    

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = UsuarioRegisterForm  
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Usuario registrado correctamente.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Itera sobre todos los errores del formulario
        for field in form:
            for error in field.errors:
                # Añade cada error como un mensaje de error
                messages.error(self.request, error)
        
        for error in form.non_field_errors():
            messages.error(self.request, error) #por ejemplo que la contra y su confirmarcion no coinciden
            
        return super().form_invalid(form)



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



class RatingView(ListView):
    model = Event
    template_name = "app/rating.html"
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
    
@login_required
def crear_rating(request, event_id):
    event= get_object_or_404(Event, pk=event_id)
    user= request.user
        
    if Rating.objects.filter(user=user, event=event).exists():
        messages.error(request, "Ya has calificado este evento.")
        return redirect('event_detail', pk=event_id)
        
    if not Ticket.objects.filter(user=user, event=event).exists():
        messages.error(request, "Debes comprar un ticket para calificar este evento.")
        return redirect('event_detail', pk=event_id)
        
    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = user
            rating.event = event
            rating.save()
            messages.success(request, "Calificación creada correctamente.")
            return redirect('event_detail', pk=event_id)
    else:
        form = RatingForm()
    return render(request, 'app/crear_rating.html', {'form': form, 'event': event}) 
        
class BuscarEventosView(ListView):
    model = Event
    template_name = "app/resultados_busqueda.html"
    context_object_name = "eventos"

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        self.query = query  # Guardamos la query para usarla en el contexto
        if query:
            return Event.objects.filter(title__icontains=query)
        return Event.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = getattr(self, 'query', '')
        return context

class MiCuentaView(TemplateView):
    template_name = "accounts/my_account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['favoritos'] = Favorito.objects.filter(user=user)
        context['refund_requests'] = RefundRequest.objects.filter(user=user)
        context['unread_notifications'] = Notification.objects.filter(user=user, read=False)
        context['tickets'] = Ticket.objects.filter(user=user)
        return context