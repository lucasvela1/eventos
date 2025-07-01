from django.test import TestCase
from django.utils import timezone
from django.db.utils import IntegrityError
from eventos_app.models import Ticket, CustomUser, Event, Type
import datetime


class TicketModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='comprador1',
            email='comprador@example.com',
            password='123456'
        )
        self.event = Event.objects.create(
            title="Evento Test",
            description="Descripción del evento",
            date=timezone.now() + datetime.timedelta(days=10),
        )

    def test_ticket_creation(self):
        """Test de creación de ticket con datos válidos"""
        ticket = Ticket.objects.create(
            ticket_code="ABC123",
            quantity=2,
            type=Type.vip,
            user=self.user,
            event=self.event,
            total=5000
        )
        self.assertEqual(ticket.ticket_code, "ABC123")
        self.assertEqual(ticket.quantity, 2)
        self.assertEqual(ticket.type, Type.vip)
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.event, self.event)
        self.assertEqual(ticket.total, 5000)
        self.assertIsNotNone(ticket.buy_date)

    def test_ticket_code_must_be_unique(self):
        """Verifica que el ticket_code sea único"""
        Ticket.objects.create(
            ticket_code="UNICO",
            quantity=1,
            type=Type.general,
            user=self.user,
            event=self.event
        )
        with self.assertRaises(IntegrityError):
            Ticket.objects.create(
                ticket_code="UNICO",
                quantity=1,
                type=Type.general,
                user=self.user,
                event=self.event
            )

    def test_ticket_str_method(self):
        """Verifica que __str__ devuelva el código del ticket"""
        ticket = Ticket.objects.create(
            ticket_code="STR123",
            quantity=1,
            type=Type.general,
            user=self.user,
            event=self.event
        )
        self.assertEqual(str(ticket), "STR123")

    def test_ticket_quantity_positive(self):
        """Verifica que se pueda guardar un ticket solo con cantidad positiva"""
        with self.assertRaises(ValueError):
            Ticket.objects.create(
                ticket_code="NEGATIVO",
                quantity=-1,
                type=Type.general,
                user=self.user,
                event=self.event
            )