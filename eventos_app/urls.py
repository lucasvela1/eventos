from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    HomeView,
    EventListView,
    EventDetailView,
    NotificationListView,
    FavoritosListView,
    RefundRequestListView,
    RatingView,
    RegisterView,
    crear_rating,
    BuscarEventosView
)
from . import views
from .forms import LoginForm, UsuarioRegisterForm

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("events/", EventListView.as_view(), name="events"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("refundRequests/", RefundRequestListView.as_view(), name="refundRequests"),
    path("favoritos/", FavoritosListView.as_view(), name="favoritos"),
    path("rating/", RatingView.as_view(), name="rating"),
    path("events/<int:event_id>/calificar/", crear_rating, name='crear_rating'),
    path('eventos/<int:event_id>/toggle_favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('buscar/', BuscarEventosView.as_view(), name='buscar_eventos'),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html",authentication_form=LoginForm), name="login"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
]