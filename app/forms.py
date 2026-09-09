from django import forms
from .models import *


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da categoria'
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