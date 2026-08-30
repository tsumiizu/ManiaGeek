from django.db import models
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
# Tirar isso quando for usar o cloudinary
from django.core.validators import FileExtensionValidator
import os
from django.utils.text import slugify


# Apagar isso depois
def upload_to(instance, filename):
    extensao = os.path.splitext(filename)[1].lower()
    if hasattr(instance, 'produto'):
        produto = instance.produto
        is_imagem = True
    else:
        produto = instance
        is_imagem = False
    nome_produto = slugify(produto.nome)

    if is_imagem:
        if instance.pk:
            numero = instance.ordem
        else:
            total = Imagem.objects.filter(produto=produto).count()
            numero = total + 1
        nome_arquivo = f"{nome_produto}-{numero}{extensao}"
        return f"produtos/{nome_produto}/{nome_arquivo}"
    else:
        nome_arquivo = f"{nome_produto}{extensao}"
        return f"produtos/{nome_produto}/{nome_arquivo}"

class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    STATUS_CHOICES_PRODUTO = [
        ('copos', 'Copos'),
        ('bottoms', 'Bottoms'), 
        ('chaveiros', 'Chaveiros')
    ]
    produto_tipo = models.CharField(
        max_length=200,
        choices=STATUS_CHOICES_PRODUTO,
        default='copos',
        null= False,
        blank= False
    )
    categoria = models.ManyToManyField(Categoria, related_name='produto')
    preco = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    # depois troque para cloudinary field
    tipos_video = ['mp4', 'mov', 'avi', 'mkv', 'webm']
    video = models.FileField(
        upload_to=upload_to,
        validators=[FileExtensionValidator(allowed_extensions=tipos_video)]
    )
    def __str__(self):
        return self.nome


class Imagem(models.Model):
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.CASCADE,
        related_name='Imagem'
    )
    imagem = models.ImageField(upload_to=upload_to)
    capa = models.BooleanField(default=False)
    def clean(self):
        LIMITE_MAXIMO_IMAGENS = 4
        if not self.pk:
            total_existente = Imagem.objects.filter(produto=self.produto).count()
            if total_existente >= LIMITE_MAXIMO_IMAGENS:
                raise ValidationError(
                    f'Este produto atingiu o limite máximo de {LIMITE_MAXIMO_IMAGENS} imagens.'
                )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.capa:
            Imagem.objects.filter(
                produto=self.produto,
                capa=True
        ).exclude(pk=self.pk).update(capa=False)