from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Q
import uuid
from django.db.models import Prefetch


from django.db import models
from datetime import timedelta
from .forms import RatingForm, UsuarioRegisterForm, CommentForm, PagoForm
from django.db import transaction
from .models import Event, Favorito, Notification, Rating, RefundRequest, Ticket, Category, Comment, Type, Pago
from .utils import obtener_eventos_destacados, obtener_eventos_proximos, actualizar_total_rating

class HomeView(TemplateView):
    template_name = "home.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home']=True
        user = self.request.user
        context['events_destacados'] = obtener_eventos_destacados()
        context['categorys'] = Category.objects.filter(is_active=True)
        events_proximos_queryset = Event.objects.filter(date__gte=now().date(), cancelado=False)
        category_id = self.request.GET.get('category_id')
        if category_id:
            try:
                category = get_object_or_404(Category, id=category_id)
                events_proximos_queryset = events_proximos_queryset.filter(categorias=category).distinct()
                # La logica del filtrado por categoria para el carrousel de eventos proximos en el home
                context['selected_category'] = category
            except:
                #Si surge un error al obtener la categoría, se obtienen los eventos próximos sin filtrar
                context['events_proximos'] = obtener_eventos_proximos()
        else:
            pass
        if user.is_authenticated:
            favoritos_ids = Favorito.objects.filter(user=user).values_list('event_id', flat=True)
            
            events_proximos_queryset = events_proximos_queryset.annotate(
                is_favorito=Case(
                    When(pk__in=list(favoritos_ids), then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
            # Ordenamos por favoritos primero, y luego por fecha
            context['events_proximos'] = events_proximos_queryset.order_by('-is_favorito', 'date')
        else:
            # Para usuarios no autenticados, solo ordenamos por fecha
            context['events_proximos'] = events_proximos_queryset.order_by('date')

        return context

class EventListView(ListView):
    model = Event #Clase que manipula la vista
    template_name = "app/events.html" #Incluyo el template que controla la vista
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.activos_para_usuario(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favoritos_ids'] = Event.objects.favoritos_ids_para_usuario(self.request.user)
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
        context['comments'] = Comment.objects.for_event(event)
        context['form'] = CommentForm()

        if user.is_authenticated:
            tiene_ticket = Ticket.objects.user_has_ticket_for_event(user, event)
            context['tiene_ticket'] = tiene_ticket
            ha_calificado = Rating.objects.filter(user=user, event=event).exists() #Revisamos si el user tiene un rating asociado
            user_can_rate = tiene_ticket and event_has_passed and not ha_calificado
            context['user_can_rate'] = user_can_rate #Si el usuario tiene ticket y el evento finalizó, no calificó aún, entonces puede calificar
        else:
            context['tiene_ticket'] = False
            context['user_can_rate'] = False
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        event = self.object

        if 'delete_comment_id' in request.POST:
            comment_id = request.POST.get('delete_comment_id')
            comment = get_object_or_404(Comment, pk=comment_id, user=user)
            comment.delete()
            return redirect('event_detail', pk=event.pk)
        
        elif 'edit_comment_id' in request.POST:
            comment_id = request.POST.get('edit_comment_id')
            new_text = request.POST.get('text','').strip()
            comment = get_object_or_404(Comment, pk=comment_id, user=user)
            if new_text:
                comment.text = new_text
                comment.save()
            return redirect('event_detail', pk=event.pk)
        else:
            form = CommentForm(request.POST)
            if user.is_authenticated and form.is_valid():
                comment = form.save(commit=False)
                comment.user = user
                comment.event = event
                comment.title = event.title
                comment.save()
                return redirect('event_detail', pk=event.pk)

            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

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
        Notification.objects.unread_notifications(self.request.user).update(read=True)
        return Notification.objects.for_user_ordered_by_priority(self.request.user)
    

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
    template_name = "app/carrito.html"

    def get(self, request, event_id):
        """
        Muestra la página para seleccionar la cantidad de tickets.
        """
        event = Event.objects.get(id=event_id)
        tickets_restantes = event.venue.capacity - event.capacidad_ocupada
        precio_vip = event.price * 1.25 #


        context = {
            "event": event,
            "tickets_restantes": tickets_restantes,
            "precio_vip": precio_vip,   #El contexto que enviamos al template
        }
        return render(request, self.template_name, context)

    def post(self, request, event_id):
        
        #Valida la cantidad de tickets, la guarda en la sesión y redirige al pago.
        
        event = Event.objects.get(id=event_id)
        
        try:
            cantidad_general = int(request.POST.get("cantidad_general", 0))
            cantidad_vip = int(request.POST.get("cantidad_vip", 0))
        except (ValueError, TypeError):
            messages.error(request, "Por favor, introduce un número válido de tickets.")
            return redirect("carrito", event_id=event_id) #Si la cantidad no es válida, redirige al carrito
        
        total_cantidad_comprada = cantidad_general + cantidad_vip
        capacidad_libre = event.venue.capacity - event.capacidad_ocupada

        if total_cantidad_comprada <= 0:
            messages.error(request, "Debes seleccionar al menos un ticket para comprar.")
            return redirect("carrito", event_id=event_id)

        if total_cantidad_comprada > capacidad_libre:
            messages.error(request, f"No hay suficientes tickets. Solo quedan {capacidad_libre} disponibles.")
            return redirect("carrito", event_id=event_id)

        # Guardamos la información en la sesión del usuario para que luego se acceda desde el pago view
        request.session['cart'] = {
            'event_id': event_id,
            'cantidad_general': cantidad_general,
            'cantidad_vip': cantidad_vip,
        }

        # Redirigimos a la nueva vista de pago
        return redirect('pago', event_id=event_id)

class PagoView(LoginRequiredMixin, View):
    login_url = "/accounts/login/" #si el usuario no está logueado, lo redirige a la página de login
    template_name = "app/pago.html"

    def _prepare_context(self, event, cart_data, form=None):

        precio_vip = event.price * 1.25
        total_a_pagar = (cart_data['cantidad_general'] * event.price) + (cart_data['cantidad_vip'] * precio_vip)
        #Quitamos el Javascript y en esta ocasión cuando quiere hacer el pago le decimos cuanto cuesta todo
        return {
            "event": event,
            "cantidad_general": cart_data['cantidad_general'],
            "cantidad_vip": cart_data['cantidad_vip'],
            "precio_vip": precio_vip,
            "total_a_pagar": total_a_pagar,
            "form": form or PagoForm(), # Usa el form con errores si existe, si no, uno nuevo
        }  #Creamos un método para preparar el contexto que se va a enviar al template con todos los atributos necesarios

    def get(self, request, event_id):
        #Resumen del pedido y formulario de pago
        cart_data = request.session.get('cart') #obtenemos el carrito de la sesión desde el request.session
        # Si no hay nada en el carrito o es de otro evento, redirigir al carrito
        if not cart_data or cart_data.get('event_id') != event_id:
            messages.warning(request, "Tu carrito está vacío o ha expirado. Por favor, selecciona tus tickets de nuevo.")
            return redirect("carrito", event_id=event_id)

        event = Event.objects.get(id=event_id)
        context = self._prepare_context(event, cart_data)
        
        return render(request, self.template_name, context)

    def post(self, request, event_id):
        #Pago y creación de tickets
        cart_data = request.session.get('cart')
        if not cart_data or cart_data.get('event_id') != event_id:
            return redirect("carrito", event_id=event_id)

        event = Event.objects.get(id=event_id)
        form = PagoForm(request.POST)

        if not form.is_valid():
            # Si el form no es válido, re-renderizamos la página de pago con los errores
            context = self._prepare_context(event, cart_data, form=form)
            return render(request, self.template_name, context)

        numero_tarjeta = form.cleaned_data["numero_tarjeta"]
        if not Pago.validar_tarjeta_luhn(numero_tarjeta):
            form.add_error("numero_tarjeta", "El número de tarjeta ingresado no es válido.")
            context = self._prepare_context(event, cart_data, form=form)
            return render(request, self.template_name, context)
        
        cantidad_general = cart_data['cantidad_general']
        cantidad_vip = cart_data['cantidad_vip']
        total_cantidad_comprada = cantidad_general + cantidad_vip
        precio_vip = event.price * 1.25
        
        with transaction.atomic():
            event_a_actualizar = Event.objects.select_for_update().get(id=event_id)
            #Le cambios la cantidad al evento, si no hay capacidad suficiente, muestra un mensaje de error
            capacidad_libre = event_a_actualizar.venue.capacity - event_a_actualizar.capacidad_ocupada
            if total_cantidad_comprada > capacidad_libre:
                messages.error(request, f"Lo sentimos, mientras realizabas la compra alguien más compró tickets. Solo quedan {capacidad_libre} disponibles.")
                return redirect("carrito", event_id=event_id)

            event_a_actualizar.capacidad_ocupada += total_cantidad_comprada
            event_a_actualizar.save()
            # Creamos los tickets, si hay compras de general un ticket con todas las cantidades de general, si hay compras de vip un ticket con todas las cantidades de vip
            if cantidad_general > 0:
                Ticket.objects.create(
                    user=request.user, event=event_a_actualizar, quantity=cantidad_general,
                    type=Type.general, total=(cantidad_general * event_a_actualizar.price),
                    ticket_code=f"GEN-{uuid.uuid4()}"
                )

            if cantidad_vip > 0:
                Ticket.objects.create(
                    user=request.user, event=event_a_actualizar, quantity=cantidad_vip,
                    type=Type.vip, total=(cantidad_vip * precio_vip),
                    ticket_code=f"VIP-{uuid.uuid4()}"
                )

            total_puntos = total_cantidad_comprada * event_a_actualizar.cantidad_puntos
            request.user.puntaje += total_puntos
            request.user.save()

            Notification.objects.create(
                user=request.user, title="Ticket comprado",
                message=f"Compraste {total_cantidad_comprada} ticket/s para {event_a_actualizar.title}.",
                priority="MEDIUM"
            )
        
        # Limpiamos el carrito de la sesión
        del request.session['cart']
        
        messages.success(request, "¡Tu compra ha sido realizada con éxito!")
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
            .order_by("-total_rating")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Eventos con ticket comprado
            tickets = Ticket.objects.filter(user=user).values_list('event_id', flat=True)
            context['eventos_con_ticket'] = set(tickets)
            # Eventos ya calificados
            ratings_qs = Rating.objects.filter(user=user)
            ratings_dict = {r.event_id: r for r in ratings_qs}
            eventos = context['events']
            for evento in eventos:
                if evento.id in ratings_dict:
                    evento.user_rating = [ratings_dict[evento.id]]
                else:
                    evento.user_rating = []
            context['eventos_ya_calificados'] = set(ratings_dict.keys())
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
        self.event.actualizar_total_rating()
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
        self.rating.event.actualizar_total_rating()
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
        evento = rating.event
        rating.delete()
        evento.actualizar_total_rating()
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
        today = now().date()
        context['today'] = today

        context['user'] = user
        context['unread_notifications'] = Notification.objects.unread_notifications(user, limit=5)
        context['total_unread'] = Notification.objects.unread_count(user)
        context['favoritos'] = Favorito.objects.filter(user=user)
        context['refund_requests'] = RefundRequest.objects.filter(user=user)
        context['tickets'] = Ticket.objects.filter(user=user)
        
        # Eventos para los que el usuario compró ticket
        eventos_con_ticket = Ticket.objects.filter(user=user).values_list('event', flat=True)
        context['eventos_con_ticket'] = eventos_con_ticket

        # Filtrar solo los eventos no finalizados y no cancelados
        tickets_eventos_activos = Ticket.objects.filter(user=user,event__date__gte=today,event__cancelado=False)
        context['tickets_eventos_activos'] = tickets_eventos_activos

        # Eventos ya calificados por el usuario
        context['eventos_ya_calificados'] = Event.objects.rated_by_user(user)
        context['eventos_a_calificar'] = Event.objects.to_be_rated_by_user(user)
        
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


