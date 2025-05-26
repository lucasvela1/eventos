from django.urls import path
from .views import (
    HomeView,
    EventListView,
    EventDetailView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("events/", EventListView.as_view(), name="events"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
]
