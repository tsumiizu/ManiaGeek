from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['email', 'username', 'display_name', 'telefone']
    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name')
        if display_name and Usuario.objects.filter(display_name=display_name).exists():
            raise forms.ValidationError("Este nome de exibição já está em uso. Por favor, escolha outro.")
        return display_name
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este e-mail já está em uso por outra conta.")   
        return email

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['display_name', 'telefone', 'email', 'foto']
        def clean_display_name(self):
            display_name = self.cleaned_data.get('display_name')
            if display_name and Usuario.objects.filter(display_name=display_name).exists():
                raise forms.ValidationError("Este nome de exibição já está em uso. Por favor, escolha outro.")
            return display_name
        def clean_email(self):
            email = self.cleaned_data.get('email')
            if email:
                if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Este e-mail já está em uso por outra conta.")
            return email

# Depois fazer model de foto de perfil 