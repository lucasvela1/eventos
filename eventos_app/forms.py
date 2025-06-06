from django import forms
from .models import Rating
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['title', 'text', 'rating']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la calificación'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu comentario'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


class LoginForm(forms.Form):
    usuario    = forms.CharField(
        label="Usuario",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingresa tu usuario"
        })
    )
    contrasena = forms.CharField(
        label="Contraseña",
        max_length=128,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Ingresa tu contraseña"
        })
    )

    def clean_usuario(self):
        valor = self.cleaned_data.get("usuario", "").strip()
        if not valor:
            raise forms.ValidationError("El campo Usuario es obligatorio.")
        return valor

    def clean_contrasena(self):
        pwd = self.cleaned_data.get("contrasena", "")
        if len(pwd) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        return pwd

    def clean(self):
        datos = super().clean()
        u = datos.get("usuario")
        p = datos.get("contrasena")


        if self.errors:
            return datos


        return datos
    

class UsuarioRegisterForm(UserCreationForm):
     email = forms.EmailField(required=True)

     class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]

     def clean_email(self):
         email = self.cleaned_data["email"]
         if CustomUser.objects.filter(email=email).exists():
             raise forms.ValidationError("Este email ya está registrado.")
         return email