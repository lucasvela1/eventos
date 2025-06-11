from django import forms
from .models import Rating
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['title', 'text', 'rating']
        labels = {
            'title': 'Título',
            'text': 'Comentario',
            'rating': 'Puntaje',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la calificación'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu comentario'}),
            #'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'rating': forms.RadioSelect(choices=[(i, f'{i} estrellas') for i in range(1, 6)]),
        }


class LoginForm(AuthenticationForm):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizamos los campos del formulario de autenticación por defecto
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Usuario'}
        )
        self.fields['username'].label = "Usuario"

        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Contraseña'}
        )
        self.fields['password'].label = "Contraseña"
    

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
     
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #Personalizamos el formulario de registro, le ponemos que queremos que salte en el error, o que pide como necesario
        self.fields['username'].label = "Usuario"
        self.fields['username'].help_text = "Usa solo letras, números y los caracteres @ . + - _"

        self.fields['email'].label = "Correo Electrónico"
        self.fields['email'].help_text = ""
        
        self.fields['password1'].label = "Contraseña"
        self.fields['password1'].help_text = "Tu contraseña debe tener al menos 8 caracteres."

        self.fields['password2'].label = "Confirmación de contraseña"
        self.fields['password2'].help_text = ""

        self.fields['username'].error_messages['unique'] = "Este nombre de usuario ya está en uso. Por favor, elige otro."
        self.fields['email'].error_messages['unique'] = "Esta dirección de correo ya fue registrada."
        self.fields['email'].error_messages['required'] = "El campo de correo es obligatorio." 
        self.fields['password1'].error_messages['required'] = "El campo de contraseña es obligatorio."
        self.fields['password2'].error_messages['required'] = "El campo de confirmación de contraseña es obligatorio."
        self.fields['password1'].error_messages['min_length'] = "La contraseña debe tener al menos 8 caracteres."

