from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from eventos_app.models import UserRole, CustomUser
#from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class CustomUserModelTest(TestCase):

    def test_create_user_with_valid_data(self):
        """Verifica que se pueda crear un CustomUser válido"""
        user = CustomUser.objects.create_user(
            username='usuario_test',
            email='test@example.com',
            password='12345678',
            puntaje=10,
            rol=UserRole.CLIENTE
        )
        self.assertEqual(user.username, 'usuario_test')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.puntaje, 10)
        self.assertEqual(user.rol, UserRole.CLIENTE)

    def test_username_required(self):
        """Verifica que no se pueda crear un usuario sin username"""
        user = CustomUser(
            username='',
            email='valido@example.com',
            puntaje=5
        )
        with self.assertRaises(ValidationError):
            user.clean()

    def test_email_required(self):
        """Verifica que no se pueda crear un usuario sin email"""
        user = CustomUser(
            username='usuario',
            email='',
            puntaje=5
        )
        with self.assertRaises(ValidationError):
            user.clean()

    def test_puntaje_negative(self):
        """Verifica que no se pueda asignar puntaje negativo"""
        user = CustomUser(
            username='usuario',
            email='usuario@example.com',
            puntaje=-10
        )
        with self.assertRaises(ValidationError):
            user.clean()

    def test_email_unique(self):
        """Verifica que no se puedan repetir emails"""
        CustomUser.objects.create_user(
            username='usuario1',
            email='repetido@example.com',
            password='123456'
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='usuario2',
                email='repetido@example.com',
                password='123456'
            )

    def test_str_method(self):
        """Verifica que __str__ devuelva el username"""
        user = CustomUser.objects.create_user(
            username='miusuario',
            email='email@example.com',
            password='123456'
        )
        self.assertEqual(str(user), 'miusuario')

    def test_default_rol(self):
        """Verifica que el rol por defecto sea CLIENTE"""
        user = CustomUser.objects.create_user(
            username='cliente',
            email='cliente@example.com',
            password='123456'
        )
        self.assertEqual(user.rol, UserRole.CLIENTE)