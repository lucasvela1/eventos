from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import (
    HomeView,
    EventListView,
    EventDetailView,
    NotificationListView,
    FavoritosListView,
    ToggleFavoritoView,
    RefundRequestListView,
    RatingView,
    RegisterView,
    CrearRatingView,
    BuscarEventosView,
    MiCuentaView,
    CarritoView, 
    EditarRatingView,
    ReembolsoView, 
    EliminarRatingView,
)

from .forms import LoginForm, UsuarioRegisterForm

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("events/", EventListView.as_view(), name="events"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("refundRequests/", RefundRequestListView.as_view(), name="refund_requests"),
    path("favoritos/", FavoritosListView.as_view(), name="favoritos"),
    path('eventos/<int:event_id>/toggle_favorito/', ToggleFavoritoView.as_view(), name='toggle_favorito'),
    path("rating/", RatingView.as_view(), name="rating"),
    path('ratings/<int:pk>/editar/', EditarRatingView.as_view(), name='editar_rating'),
    path("events/<int:event_id>/calificar/", CrearRatingView.as_view(), name='crear_rating'),
    path('rating/eliminar/<int:pk>/', EliminarRatingView.as_view(), name='eliminar_rating'),
    path('buscar/', BuscarEventosView.as_view(), name='buscar_eventos'),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html",authentication_form=LoginForm), name="login"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/register/usuario/", MiCuentaView.as_view(), name="my_account" ),
    path('carrito/<int:event_id>/', CarritoView.as_view(), name='carrito'),
    path("reembolso/<str:ticket_code>/", ReembolsoView.as_view(), name="reembolso"),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

