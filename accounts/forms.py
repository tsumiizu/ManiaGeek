from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Força o display name e o telefone a serem null
        self.fields['display_name'].required = False
        self.fields['telefone'].required = False

        self.fields['email'].error_messages = {
            'required': 'Informe um e-mail.',
            'invalid': 'Digite um e-mail válido.',
            'unique': 'Este e-mail já está em uso por outra conta.',
        }
        self.fields['username'].error_messages = {
            'required': 'Escolha um nome de usuário.',
            'unique': 'Este nome de usuário já está em uso.',
            'invalid': 'Use apenas letras, números e os caracteres @ . + - _',
        }
        self.fields['password1'].error_messages = {
            'required': 'Crie uma senha.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Confirme a senha.',
        }
    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name')
        if display_name and Usuario.objects.filter(display_name=display_name).exists():
            raise forms.ValidationError(
                "Este nome de exibição já está em uso. Por favor, escolha outro."
            )
        return display_name
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Este e-mail já está em uso por outra conta."
            )
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
        usuario.set_password(self.cleaned_data["password1"])
        if commit:
            usuario.save()
        return usuario

class CodigoVerificacaoForm(forms.Form):
    codigo = forms.CharField(
        label="Código",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
            'autofocus': True,
        }),
    )
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip()
        if not codigo.isdigit():
            raise forms.ValidationError("O código contém apenas números.")
        return codigo

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['display_name', 'telefone', 'email']
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

class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['foto']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._foto_antiga = None
        if self.instance and self.instance.pk:
            self._foto_antiga = self.instance.foto
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if not foto:
            return foto
        if not self.instance.pode_alterar():
            raise ValidationError(
                "Você já atingiu o limite de 3 trocas de foto neste mês. "
                "Tente novamente no próximo mês."
            )
        if foto.size > 5 * 1024 * 1024:
            raise ValidationError("A imagem não pode passar de 5MB.")
        return foto
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            usuario.registrar_troca_foto()
            usuario.save(update_fields=['limite_alteracao', 'ultima_foto'])
            usuario.deletar_cloudinary(self._foto_antiga)
        return usuario