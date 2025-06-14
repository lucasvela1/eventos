from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Avg, Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.utils.timezone import now
from django.db.models import Q, Avg
import uuid
from django.db.models import Prefetch

from django.db import models
from datetime import timedelta
from .forms import RatingForm, UsuarioRegisterForm
from django.db import transaction
from .models import Event, Favorito, Notification, Rating, RefundRequest, Ticket, Category
from .utils import obtener_eventos_destacados, obtener_eventos_proximos




class HomeView(TemplateView):
    template_name = "home.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events_destacados'] = obtener_eventos_destacados()
        context['events_proximos'] = obtener_eventos_proximos()
        context['categorys'] = Category.objects.filter(is_active=True)
        return context

class EventListView(ListView):
    model = Event #Clase que manipula la vista
    template_name = "app/events.html" #Incluyo el template que controla la vista
    context_object_name = "events"

    def get_queryset(self): #Pasarle una lista distinta al context
        today = now().date()
        return Event.objects.filter(date__gte=today, cancelado=False).order_by("date")

    def get_context_data(self, **kwargs):  #Llamo al context data del padre, me traigo todos los objetos de event
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            favoritos_ids = Favorito.objects.filter(user=user).values_list('event_id', flat=True)
            context['favoritos_ids'] = list(favoritos_ids)
        else:
            context['favoritos_ids'] = []
        return context  
    
class EventDetailView(DetailView):
    model = Event
    template_name = "app/event_detail.html"
    context_object_name = "event"

class NotificationListView(LoginRequiredMixin, ListView):
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
        return Notification.objects.filter(user=self.request.user).order_by(priority_order, "-created_at") 
         #filtrar notificaciones por usuario
         # Ordena las notificaciones por prioridad y luego por fecha de creación, de más reciente a más antiguo

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
    
class CarritoView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def get(self, request, event_id):
      event = Event.objects.get(id=event_id)
      tickets_restantes = event.venue.capacity - event.capacidad_ocupada
      return render(request, "app/carrito.html", {
        "event": event,
        "tickets_restantes": tickets_restantes,
    })

    def post(self, request, event_id):
       event = Event.objects.get(id=event_id)
       cantidad = int(request.POST.get("cantidad", 1))

       if cantidad < 1:
         return redirect("carrito", event_id=event_id)
       #Por más que en el html no aparezca para poner menos a 0, o 0. Se puede manipular y enviar de alguna forma
       #un valor que no corresponde, por eso con esto validamos en nuestra parte "backend"
       
       with transaction.atomic():
           capacidad_libre = event.venue.capacity - event.capacidad_ocupada
           if cantidad > capacidad_libre:
                #messages.error(self.request, f"Hay {capacidad_libre} tickets restantes para este event.")
                return redirect("carrito", event_id=event_id)
           
       event.capacidad_ocupada+=cantidad
       event.save()
       Ticket.objects.create(
            user=request.user,
            event=event,
            quantity=cantidad,
            total=cantidad * event.price,
            ticket_code=str(uuid.uuid4())
        ) 

       #messages.success(self.request, f"{cantidad} ticket(s) comprados correctamente.")
       Notification.objects.create(
           user=request.user,
           title="Ticket comprado",
           message=f"Se ha comprado exitosamente {cantidad} ticket/s para {event.title}",
           priority="MEDIUM"
       )
       return redirect("my_account")

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = UsuarioRegisterForm  
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

class RefundRequestListView(ListView):
    model = RefundRequest
    template_name = "app/refundRequest.html"
    context_object_name = "refund_requests"

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
        yesterday = now().date() - timedelta(days=1)
        return (
            Event.objects
            .filter(Q(date__lt=yesterday) | Q(cancelado=True))  # Eventos finalizados o cancelados
            .annotate(rating_promedio=Avg("rating__rating"))  # Calcula el promedio de ratings
            .order_by("-rating_promedio")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Eventos con ticket comprado
            tickets = Ticket.objects.filter(user=user).values_list('event_id', flat=True)
            # Eventos ya calificados
            ratings = Rating.objects.filter(user=user).values_list('event_id', flat=True)
            context['eventos_con_ticket'] = set(tickets)
            context['eventos_ya_calificados'] = set(ratings)
        else:
            context['eventos_con_ticket'] = set()
            context['eventos_ya_calificados'] = set()

        return context
    
class CrearRatingView(LoginRequiredMixin, FormView):
    template_name = 'app/crear_rating.html'
    form_class = RatingForm

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs['event_id'])
        self.user = request.user

        # Ya calificó
        if Rating.objects.filter(user=self.user, event=self.event).exists():
            #messages.error(request, "Ya has calificado este evento.")
            return redirect('event_detail', pk=self.event.pk)

        # No compró ticket
        if not Ticket.objects.filter(user=self.user, event=self.event).exists():
            #messages.error(request, "Debes comprar un ticket para calificar este evento.")
            return redirect('event_detail', pk=self.event.pk)
        
        # Solo permitir si el evento ya finalizó o fue cancelado
        today = now().date() 
        if self.event.date > today and not self.event.cancelado:
            #messages.error(request, "Solo puedes calificar eventos finalizados o cancelados.")
            return redirect('event_detail', pk=self.event.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        rating = form.save(commit=False)
        rating.user = self.user
        rating.event = self.event
        rating.save()
        #messages.success(self.request, "Calificación creada correctamente.")
        return redirect('event_detail', pk=self.event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

class EditarRatingView(LoginRequiredMixin, UpdateView):
    model = Rating
    form_class = RatingForm
    template_name = 'app/editar_rating.html'
    context_object_name = 'rating'

    def dispatch(self, request, *args, **kwargs):
        self.rating = get_object_or_404(Rating, pk=kwargs['pk'])

        if self.rating.user != request.user:
            messages.error(request, "No tienes permiso para editar esta calificación.")
            return redirect('event_detail', pk=self.rating.event.pk)

        # Solo permitir edición si el evento finalizó o fue cancelado
        today = now().date()
        if self.rating.event.date > today and not self.rating.event.cancelado:
            messages.error(request, "Solo puedes editar calificaciones de eventos finalizados o cancelados.")
            return redirect('event_detail', pk=self.rating.event.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Calificación actualizada correctamente.")
        return redirect('event_detail', pk=self.rating.event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.rating.event
        return context 

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
        unread_notifications = Notification.objects.filter(user=user, read=False).order_by('-created_at')[:5]
        context['unread_notifications'] = unread_notifications
        context['total_unread'] = Notification.objects.filter(user=user, read=False).count()
        context['tickets'] = Ticket.objects.filter(user=user)
        today = now().date()
        # Eventos para los que el usuario compró ticket
        eventos_con_ticket = Ticket.objects.filter(user=user).values_list('event', flat=True)

        # Filtrar solo los eventos no finalizados y no cancelados
        tickets_eventos_activos = Ticket.objects.filter(user=user,event__date__gte=today,event__cancelado=False)

        # Eventos ya calificados por el usuario
        user_ratings = Rating.objects.filter(user=user)
        eventos_ya_calificados = Event.objects.filter(rating__user=user).prefetch_related(
            Prefetch('rating_set', queryset=user_ratings, to_attr='user_rating')
        ).distinct()

        # Eventos para calificar: con ticket comprado, que ya finalizaron o fueron cancelados,
        # y que el usuario no haya calificado aún
        eventos_a_calificar = Event.objects.filter(
            id__in=eventos_con_ticket
        ).exclude(
            id__in=eventos_ya_calificados
        ).filter(
            models.Q(cancelado=True) | models.Q(date__lt=today)  # Eventos cancelados o pasados
        )
        context['eventos_con_ticket'] = eventos_con_ticket
        context['eventos_a_calificar'] = eventos_a_calificar
        context['eventos_ya_calificados'] = eventos_ya_calificados
        context['tickets_eventos_activos'] = tickets_eventos_activos

        return context
    


class ReembolsoView(LoginRequiredMixin, View):
    def get(self, request, ticket_code):
        ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)

        ya_solicitado = RefundRequest.objects.filter(ticket_code=ticket.ticket_code).exists()
        evento_pasado = ticket.event.date <= now().date()

        return render(request, "app/reembolso.html", {
            "ticket": ticket,
            "ya_solicitado": ya_solicitado,
            "evento_pasado": evento_pasado
        })

    def post(self, request, ticket_code):
        ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)

        if ticket.event.date > now().date():
            return redirect("my_account")
        
        if RefundRequest.objects.filter(ticket_code=ticket.ticket_code).exists():
            return redirect("my_account")

        reason = request.POST.get("reason", "").strip()
        if not reason:
            return redirect("reembolso", ticket_code=ticket.ticket_code)


        RefundRequest.objects.create(
            approved=False,  # Se aprueba más tarde manualmente
            ticket_code=ticket.ticket_code,
            reason=reason,
            user=request.user
        )

        Notification.objects.create(
            user=request.user,
            title="Reembolso solicitado",
            message=f"Se ha solicitado el reembolso para el evento {ticket.event.title}.",
            priority="HIGH"
        )

        return redirect("my_account")


class AceptarReembolsoView(PermissionRequiredMixin, View):
    permission_required = 'app_name.can_accept_refund'

