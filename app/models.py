from django.db import models
from django.conf import settings
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

class Endereco(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enderecos')
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)

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
    quantidade = models.PositiveBigIntegerField(default=1)
    categoria = models.ManyToManyField(Categoria, related_name='produto')
    preco = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    descricao = models.TextField()
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
    alt_text = models.CharField(max_length=255, null=False, blank=False)
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

# Por equanto é a "postagem"
class Anuncio(models.Model):
    titulo = models.CharField(max_length=200, null=False, blank=False)
    descricao = models.TextField()
    imagem = models.ImageField(upload_to='postagens/')

# O models de review vai ter o foreign key dos produtos, mas pode ser bom pra reutilizar para os reviews da loja em geral... pode ter 2 campos
# Ou pode ter algo mais robusto como reviews inteligentes interligando o email 