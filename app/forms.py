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
            'capa',
            'alt_text_capa',
            'video',
            'destaque'
        ]
        labels = {
            'nome': 'Nome do Produto',
            'produto_tipo': 'Tipo de Produto',
            'quantidade': 'Estoque (Quantidade)',
            'categoria': 'Categorias (Selecione uma ou mais)',
            'preco': 'Preço (R$)',
            'descricao': 'Descrição',
            'capa': 'Capa do Produto',
            'alt_text_capa': 'Texto Alternativo da Capa',
            'video': 'Vídeo Demonstrativo (Opcional)',
            'destaque': 'Se o produto vai aparecer como destaque no carrossel da pagina inicial'
        }
class ProdutoImagemForm(forms.ModelForm):
    class Meta:
        model = Imagem
        fields = ['imagem', 'alt_text']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'alt_text': forms.TextInput(attrs={
                'placeholder': 'Texto alternativo da imagem',
            }),
        }