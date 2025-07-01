from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from eventos_app.models import Notification, Priority
from eventos_app.managers import NotificationManager  

CustomUser = get_user_model()


class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_notification_creation(self):
        """Verifica que se pueda crear una notificación correctamente"""
        notification = Notification.objects.create(
            title="Prueba de notificación",
            message="Este es el mensaje de prueba",
            priority=Priority.medium,
            user=self.user
        )

        self.assertEqual(notification.title, "Prueba de notificación")
        self.assertEqual(notification.message, "Este es el mensaje de prueba")
        self.assertEqual(notification.priority, Priority.medium)
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.read)
        self.assertIsNotNone(notification.created_at)

    def test_notification_str(self):
        """Verifica que el método __str__ devuelva el título"""
        notification = Notification.objects.create(
            title="Título visible",
            message="Mensaje",
            priority=Priority.medium,
            user=self.user
        )
        self.assertEqual(str(notification), "Título visible")

    def test_notification_default_read_value(self):
        """Verifica que el valor por defecto de 'read' sea False"""
        notification = Notification.objects.create(
            title="No leída",
            message="Mensaje",
            priority=Priority.high,
            user=self.user
        )
        self.assertFalse(notification.read)

    def test_notification_user_required(self):
        """Verifica que no se pueda crear una notificación sin usuario si blank=False"""
        with self.assertRaises(Exception):
            Notification.objects.create(
                title="Sin usuario",
                message="Mensaje",
                priority=Priority.medium,
                user=None  # Esto debería lanzar error si blank=False
            )