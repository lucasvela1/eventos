from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from eventos_app.models import Pago, Event

CustomUser = get_user_model()

class PagoModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='comprador',
            email='comprador@example.com',
            password='123456'
        )
        self.event = Event.objects.create(
            title='Evento Prueba',
            description='Evento para testing',
            date=timezone.now() + timezone.timedelta(days=5),
        )

    def test_pago_creation_valid(self):
        """Verifica que se cree correctamente un pago válido"""
        pago = Pago.objects.create(
            user=self.user,
            event=self.event,
            nombre_titular="Juan Pérez",
            numero_tarjeta="4539578763621486",  # válida con Luhn
            fecha_vencimiento="12/26",
            cvv="123",
            monto=2500.00
        )
        self.assertEqual(pago.user, self.user)
        self.assertEqual(pago.event, self.event)
        self.assertEqual(pago.nombre_titular, "Juan Pérez")
        self.assertEqual(pago.numero_tarjeta, "4539578763621486")
        self.assertEqual(pago.fecha_vencimiento, "12/26")
        self.assertEqual(pago.cvv, "123")
        self.assertEqual(pago.monto, 2500.00)
        self.assertIsNotNone(pago.fecha_creacion)

    def test_pago_str_method(self):
        """Verifica que __str__ devuelva correctamente la descripción del pago"""
        pago = Pago.objects.create(
            user=self.user,
            event=self.event,
            nombre_titular="Ana López",
            numero_tarjeta="4539578763621486",
            fecha_vencimiento="01/25",
            cvv="321",
            monto=1999.99
        )
        self.assertEqual(str(pago), f"Pago de {self.user.username} por $1999.99")

    def test_tarjeta_valida_luhn(self):
        """Verifica que una tarjeta válida pase el algoritmo de Luhn"""
        valida = Pago.validar_tarjeta_luhn("4539578763621486")
        self.assertTrue(valida)

    def test_tarjeta_invalida_luhn(self):
        """Verifica que una tarjeta inválida falle el algoritmo de Luhn"""
        invalida = Pago.validar_tarjeta_luhn("1234567890123456")
        self.assertFalse(invalida)

    def test_tarjeta_con_espacios_o_guiones(self):
        """Verifica que la validación Luhn funcione con espacios o guiones"""
        self.assertTrue(Pago.validar_tarjeta_luhn("4539 5787 6362 1486"))
        self.assertTrue(Pago.validar_tarjeta_luhn("4539-5787-6362-1486"))