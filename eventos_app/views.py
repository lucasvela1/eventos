from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Q, Avg
import uuid
from django.db.models import Prefetch


from django.db import models
from datetime import timedelta
from .forms import RatingForm, UsuarioRegisterForm, CommentForm
from django.db import transaction
from .models import Event, Favorito, Notification, Rating, RefundRequest, Ticket, Category, Comment, Type
from .utils import obtener_eventos_destacados, obtener_eventos_proximos, actualizar_total_rating




class HomeView(TemplateView):
    template_name = "home.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events_destacados'] = obtener_eventos_destacados()
        context['categorys'] = Category.objects.filter(is_active=True)
        category_id = self.request.GET.get('category_id')
        if category_id:
            try:
                category = get_object_or_404(Category, id=category_id)
                # La logica del filtrado por categoria para el carrousel de eventos proximos en el home
                context['events_proximos'] = Event.objects.filter(
                    date__gte=now().date(),
                    cancelado=False,
                    categoria=category
                ).order_by("date") #Los ordenamos por su fecha
                context['selected_category'] = category #Se envia la categoría seleccionada al template
            except:
                #Si surge un error al obtener la categoría, se obtienen los eventos próximos sin filtrar
                context['events_proximos'] = obtener_eventos_proximos()
        else:
           context['events_proximos'] = obtener_eventos_proximos()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        user = self.request.user
        event_has_passed = event.date < timezone.now().date()
        context['event_has_passed'] = event_has_passed
        context['comments'] = Comment.objects.filter(event = event).order_by('-created_at')
        context['form'] = CommentForm()

        if user.is_authenticated:
            tiene_ticket = Ticket.objects.filter(user=user, event=event).exists()
            context['tiene_ticket'] = Ticket.objects.filter(user=user, event=event).exists()
            ha_calificado = Rating.objects.filter(user=user, event=event).exists()
            user_can_rate = tiene_ticket and event_has_passed and not ha_calificado
            context['user_can_rate'] = user_can_rate
        else:
            context['tiene_ticket'] = False
            context['user_can_rate'] = False
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if request.user.is_authenticated and form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.event = self.object
            comment.title = self.object.title
            comment.save()

            return redirect('event_detail', pk=self.object.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'app/edit_comment.html'

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.event.pk})

    def test_func(self):
        return self.request.user == self.get_object().user

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'app/delete_comment.html'

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.get_object().event.pk})

    def test_func(self):
        return self.request.user == self.get_object().user


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "app/notification.html"
    context_object_name = "notifications"

    def get_queryset(self):
        priority_order = Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
        
        queryset = Notification.objects.filter(user=self.request.user).order_by(priority_order, "-created_at")
        
        queryset.filter(read=False).update(read=True)
        return queryset
    
class EliminarNotificacionesSeleccionadasView(LoginRequiredMixin, View):
    def post(self, request):
        ids_a_eliminar = request.POST.getlist("notificaciones")
        Notification.objects.filter(user=request.user, id__in=ids_a_eliminar).delete()
        return redirect("notifications")
    
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
        precio_vip = event.price * 1.25
        tickets_restantes = event.venue.capacity - event.capacidad_ocupada
        return render(request, "app/carrito.html", {
            "event": event,
            "tickets_restantes": tickets_restantes,
            "tickets_vip": precio_vip,
        })

    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)
        cantidad = int(request.POST.get("cantidad", 1))

        try:
            cantidad_general = int(request.POST.get("cantidad_general", 0))
            cantidad_vip = int(request.POST.get("cantidad_vip", 0))
        except (ValueError, TypeError):
            messages.error(request, "Por favor, introduce un número válido de tickets.")
            return redirect("carrito", event_id=event_id)

        total_cantidad_comprada = cantidad_general + cantidad_vip

        if total_cantidad_comprada <= 0:
            messages.error(request, "Debes seleccionar al menos un ticket para comprar.")
            return redirect("carrito", event_id=event_id)

        precio_vip = event.price * 1.25

        with transaction.atomic():
            event_a_actualizar = Event.objects.select_for_update().get(id=event_id)
            
            capacidad_libre = event_a_actualizar.venue.capacity - event_a_actualizar.capacidad_ocupada
            if total_cantidad_comprada > capacidad_libre:
                messages.error(request, f"No hay suficientes tickets. Solo quedan {capacidad_libre} disponibles.")
                return redirect("carrito", event_id=event_id)
            event_a_actualizar.capacidad_ocupada += total_cantidad_comprada
            event_a_actualizar.save()
            #Por como esta hecho, crea dos tickets, uno general y otro vip con sus cantidades, si se compran ambos tipos
            if cantidad_general > 0:
                Ticket.objects.create(
                    user=request.user,
                    event=event_a_actualizar,
                    quantity=cantidad_general,
                    type=Type.general,  
                    total=cantidad_general * event_a_actualizar.price,
                    ticket_code=f"GEN-{uuid.uuid4()}" # Código único con prefijo GEN para diferenciar de los vips
                )

            if cantidad_vip > 0:
                Ticket.objects.create(
                    user=request.user,
                    event=event_a_actualizar,
                    quantity=cantidad_vip,
                    type=Type.vip,  
                    total=cantidad_vip * precio_vip,
                    ticket_code=f"VIP-{uuid.uuid4()}" # Código único con prefijo VIP para diferenciar de los generales
                )

            Notification.objects.create(
                user=request.user,
                title="Ticket comprado",
                message=f"Compraste {total_cantidad_comprada} ticket/s para {event_a_actualizar.title}.",
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
        actualizar_total_rating(self.event)
        return redirect(reverse_lazy('my_account'))

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
        actualizar_total_rating(self.rating.event)
        messages.success(self.request, "Calificación actualizada correctamente.")
        return redirect(reverse_lazy('my_account'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.rating.event
        return context 

class EliminarRatingView(LoginRequiredMixin, View):
    template_name = 'accounts/confirm_delete.html'
    def get(self, request, pk):
        rating = get_object_or_404(Rating, pk=pk, user=request.user)
        return render(request, self.template_name, {'rating': rating})

    def post(self, request, pk):
        rating = get_object_or_404(Rating, pk=pk, user=request.user)
        rating.delete()
        return redirect(reverse_lazy('my_account'))

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

        return render(request, "app/reembolso.html", {
            "ticket": ticket,
            "ya_solicitado": ya_solicitado
        })

    def post(self, request, ticket_code):
        ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)

        if RefundRequest.objects.filter(ticket_code=ticket.ticket_code).exists():
            return redirect("my_account")  # o mostrar mensaje de error

        reason = request.POST.get("reason")

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

