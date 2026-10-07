from django import forms
from .models import *

class EnderecoForm(forms.ModelForm):
    """Form de endereço. Sem widgets com classe — o template escreve
    os inputs manualmente, igual ao login, pra herdar o estilo base
    do auth-card. Bootstrap fora daqui."""
    class Meta:
        model = Endereco
        fields = ['apelido', 'cep', 'endereco', 'numero',
                  'complemento', 'bairro', 'cidade', 'estado']
        labels = {
            'apelido': 'Apelido (opcional)',
            'cep': 'CEP',
            'endereco': 'Endereço',
            'numero': 'Número',
            'complemento': 'Complemento (opcional)',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado (UF)',
        }

    def clean_estado(self):
        uf = self.cleaned_data.get('estado', '').strip().upper()
        if uf and len(uf) != 2:
            raise forms.ValidationError("Use a sigla do estado (ex: RJ, SP).")
        return uf

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '').strip()
        if cep:
            apenas_digitos = ''.join(filter(str.isdigit, cep))
            if len(apenas_digitos) != 8:
                raise forms.ValidationError("CEP deve ter 8 dígitos.")
            cep = f"{apenas_digitos[:5]}-{apenas_digitos[5:]}"
        return cep

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'imagem']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Jogos, Canecas, Pixel Art...'
            }),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome',
            'produto_tipo',
            'quantidade',
            'categoria',
            'preco',
            'descricao',
            'video',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto'
            }),
            'produto_tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'categoria': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do produto...'
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
        }
        labels = {
            'nome': 'Nome do Produto',
            'produto_tipo': 'Tipo de Produto',
            'quantidade': 'Estoque (Quantidade)',
            'categoria': 'Categorias (Selecione uma ou mais)',
            'preco': 'Preço (R$)',
            'descricao': 'Descrição',
            'video': 'Vídeo Demonstrativo (Opcional)',
        }