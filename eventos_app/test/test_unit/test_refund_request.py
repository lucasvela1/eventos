from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from eventos_app.models import RefundRequest

CustomUser = get_user_model()

class RefundRequestModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='comprador',
            email='comprador@example.com',
            password='123456'
        )

    def test_create_refund_request_valid(self):
        """Verifica que se pueda crear una solicitud de reembolso válida"""
        refund = RefundRequest.objects.create(
            approved=False,
            ticket_code="REFUND123",
            reason="No pude asistir al evento",
            user=self.user
        )
        self.assertEqual(refund.ticket_code, "REFUND123")
        self.assertEqual(refund.reason, "No pude asistir al evento")
        self.assertFalse(refund.approved)
        self.assertEqual(refund.user, self.user)
        self.assertIsNotNone(refund.created_at)
        self.assertIsNone(refund.approval_date)

    def test_ticket_code_must_be_unique(self):
        """Verifica que ticket_code sea único"""
        RefundRequest.objects.create(
            approved=False,
            ticket_code="UNICO123",
            reason="Razón",
            user=self.user
        )
        with self.assertRaises(IntegrityError):
            RefundRequest.objects.create(
                approved=True,
                ticket_code="UNICO123",
                reason="Otra razón",
                user=self.user
            )

    def test_approval_date_optional(self):
        """Verifica que se pueda crear sin approval_date"""
        refund = RefundRequest.objects.create(
            approved=False,
            ticket_code="FECHALIBRE",
            reason="Prueba sin fecha",
            user=self.user
        )
        self.assertIsNone(refund.approval_date)

    def test_str_method(self):
        """Verifica que __str__ devuelva el ticket_code"""
        refund = RefundRequest.objects.create(
            approved=False,
            ticket_code="CODE123",
            reason="Test",
            user=self.user
        )
        self.assertEqual(str(refund), "CODE123")