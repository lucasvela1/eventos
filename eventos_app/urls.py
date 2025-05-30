from django.urls import path
from .views import (
    HomeView,
    EventListView,
    EventDetailView,
    NotificationListView,
    FavoritosListView,
)
from . import views

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("events/", EventListView.as_view(), name="events"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("favoritos/", FavoritosListView.as_view(), name="favoritos"),
    path('eventos/<int:event_id>/toggle_favorito/', views.toggle_favorito, name='toggle_favorito'),
]