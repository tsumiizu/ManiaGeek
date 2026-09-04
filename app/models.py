from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from cloudinary.models import CloudinaryField
from cloudinary.utils import cloudinary_url
import random
from django.utils.text import slugify

DEFAULTS = [
    'default08',
    'default13',
    'default18',
    'default19',
    'default14',
]
def get_random_avatar():
    return random.choice(DEFAULTS)

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
    capa = CloudinaryField(
        resource_type="image",
        folder='capas_produto/',
        blank=True,
        null=True
    )
    alt_text_capa = models.CharField(max_length=255, default='imagem do produto', null=False, blank=False)
    destaque = models.BooleanField(default=False)
    tipos_video = ['mp4', 'mov', 'avi', 'mkv', 'webm']
    video = CloudinaryField( 
        resource_type="video",
        folder='videos_produto/',
        blank=True,
        null=True,
    )
    def clean(self):
        super().clean()
        if self.destaque:
            qs = Produto.objects.filter(destaque=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk) 
            if qs.count() >= 5:
                raise ValidationError({
                    'destaque': 'Você já atingiu o limite de 5 produtos em destaque no carrossel. Remova alguns antes de adicionar outros'
                })
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk and not self.capa:
            self.capa = get_random_avatar()
        super().save(*args, **kwargs)
    @property
    def imagem_capa(self):
        if not self.capa:
            url, _ = cloudinary_url(get_random_avatar(), secure=True)
            return url
        if hasattr(self.capa, 'url') and self.capa.url:
            return self.capa.url
        foto_str = str(self.capa)
        url, _ = cloudinary_url(foto_str, secure=True)
        return url
    def __str__(self):
        return self.nome


class Imagem(models.Model):
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.CASCADE,
        related_name='Imagem'
    )
    imagem = CloudinaryField( 
            resource_type="image",
            folder='imagens_produto/',
            default='samples/man-portrait',
            blank=False,
            null=False
        )
    alt_text = models.CharField(max_length=255, null=False, blank=False)
    def clean(self):
        LIMITE_MAXIMO_IMAGENS = 3
        if not self.pk:
            total_existente = Imagem.objects.filter(produto=self.produto).count()
            if total_existente >= LIMITE_MAXIMO_IMAGENS:
                raise ValidationError(
                    f'Este produto atingiu o limite máximo de {LIMITE_MAXIMO_IMAGENS} imagens.'
                )

# Por equanto é a "postagem"
class Anuncio(models.Model):
    titulo = models.CharField(max_length=200, null=False, blank=False)
    descricao = models.TextField()
    imagem = CloudinaryField( 
            resource_type="image",
            folder='postagens/',
            blank=True,
            null=True
        )

# O models de review vai ter o foreign key dos produtos, mas pode ser bom pra reutilizar para os reviews da loja em geral... pode ter 2 campos
# Ou pode ter algo mais robusto como reviews inteligentes interligando o email 