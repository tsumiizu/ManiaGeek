from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UserRegisterForm(UserCreationForm):
    password1 = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput, 
        required=True
    )
    password2 = forms.CharField(
        label="Confirmar Senha", 
        widget=forms.PasswordInput, 
        required=True
    )
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
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "As senhas não coincidem.")
        return cleaned_data
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password1"])  # Aplica o hash na senha
        if commit:
            usuario.save()
        return usuario

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

# class FotoPerfilForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         fields = ['foto']