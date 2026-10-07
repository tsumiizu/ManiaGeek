from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from cloudinary.models import CloudinaryField
from cloudinary.utils import cloudinary_url
import random
from django.utils import timezone
from django.utils.text import slugify

DEFAULTS = [
    'default08',
    'default13',
    'default18',
    'default19',
    'default14',
    'default21',
]
def get_random_avatar():
    return random.choice(DEFAULTS)

class Endereco(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enderecos')
    apelido = models.CharField(max_length=255, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)

class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    imagem = CloudinaryField(
        resource_type="image",
            folder='categorias/',
            blank=True,
            null=True
    )
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk and not self.imagem:
            self.imagem = get_random_avatar()
        super().save(*args, **kwargs)
    @property
    def imagem_categoria(self):
        if not self.imagem:
            url, _ = cloudinary_url(get_random_avatar(), secure=True)
            return url
        if hasattr(self.imagem, 'url') and self.imagem.url:
            return self.imagem.url
        foto_str = str(self.imagem)
        url, _ = cloudinary_url(foto_str, secure=True)
        return url
    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    STATUS_CHOICES_PRODUTO = [
        ('canecas', 'Canecas'),
        ('brincos', 'Brincos'),
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
            default='default08',
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


# Carrinho

class Carrinho(models.Model):
    STATUS = [ # Total inutilidade 
        ('ativo', 'Ativo'),
        ('convertido', 'Convertido em Pedido'),
        ('abandonado', 'Abandonado'),
    ]
    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='carrinhos',
    )
    # session_key do Django — identifica visitante anônimo. Quando o
    # usuário loga, o carrinho anônimo é migrado pra ele.
    session_key = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default='ativo')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        # Garante 1 carrinho ativo por usuário logado.
        constraints = [
            models.UniqueConstraint(
                fields=['usuario'],
                condition=models.Q(status='ativo') & models.Q(usuario__isnull=False),
                name='unique_carrinho_ativo_por_usuario',
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                condition=models.Q(status='ativo') & models.Q(session_key__isnull=False),
                name='unique_carrinho_ativo_por_session',
            ),
        ]
    @classmethod
    def obter_para_request(cls, request):
        # Vê quem está acessando o carrinho
        if request.user.is_authenticated:
            carrinho, _ = cls.objects.get_or_create(
                usuario=request.user,
                status='ativo',
                defaults={'session_key': None},
            )
            return carrinho
        # Anônimo: precisa de session_key. Django cria na primeira escrita.
        if not request.session.session_key:
            request.session.create()
        carrinho, _ = cls.objects.get_or_create(
            session_key=request.session.session_key,
            status='ativo',
            defaults={'usuario': None},
        )
        return carrinho

    def migrar_para_usuario(self, usuario):
        if self.usuario_id == usuario.id:
            return self  # já é dele, nada a fazer
        carrinho_existente = Carrinho.objects.filter(
            usuario=usuario, status='ativo'
        ).first()
        if not carrinho_existente:
            # Não tinha carrinho logado: esse vira o dele.
            self.usuario = usuario
            self.session_key = None
            self.save(update_fields=['usuario', 'session_key'])
            return self
        # Já tinha: mescla itens do anônimo no logado
        for item in self.itens.all():
            item_existente = carrinho_existente.itens.filter(
                produto=item.produto
            ).first()
            if item_existente:
                item_existente.quantidade += item.quantidade
                item_existente.save(update_fields=['quantidade'])
            else:
                item.carrinho = carrinho_existente
                item.save(update_fields=['carrinho'])
        self.status = 'abandonado'
        self.save(update_fields=['status'])
        return carrinho_existente
    @property
    def subtotal(self):
        return sum(
            item.subtotal for item in self.itens.all() if item.produto is not None
        )
    @property
    def quantidade_total(self):
        return sum(item.quantidade for item in self.itens.all())
    @property
    def tem_indisponivel(self):
        return self.itens.filter(produto__isnull=True).exists()
    @property
    def tem_sem_estoque(self):
        return self.itens.filter(
            produto__isnull=False, produto__quantidade=0
        ).exists()

    @property
    def pode_fechar(self):
        return (
            self.itens.exists()
            and not self.tem_indisponivel
            and not self.tem_sem_estoque
        )
    def __str__(self):
        dono = self.usuario.email if self.usuario else f"anônimo ({self.session_key})"
        return f"Carrinho #{self.pk} - {dono}"
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(
        Carrinho,
        on_delete=models.CASCADE,
        related_name='itens',
    )
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='itens_carrinho',
    )
    # Snapshot — preenchido na criação, atualizado quando o usuário
    # revisita o carrinho e o preço/nome mudou.
    nome_produto = models.CharField(max_length=255)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    imagem_url = models.URLField(max_length=500, blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    adicionado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        # Um produto só aparece uma vez por carrinho. Adicionar de novo
        # soma na quantidade em vez de criar linha nova.
        constraints = [
            models.UniqueConstraint(
                fields=['carrinho', 'produto'],
                condition=models.Q(produto__isnull=False),
                name='unique_produto_por_carrinho',
            ),
        ]
        ordering = ['adicionado_em']
    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade
    @property
    def disponivel(self):
        return self.produto is not None and self.produto.quantidade > 0
    @property
    def preco_mudou(self):
        """True se o preço atual é diferente do snapshot."""
        if self.produto is None:
            return False
        return self.produto.preco != self.preco_unitario

    def sincronizar_com_produto(self):
        if self.produto is None:
            return
        atualizou = False
        if self.nome_produto != self.produto.nome:
            self.nome_produto = self.produto.nome
            atualizou = True
        if self.preco_unitario != self.produto.preco:
            self.preco_unitario = self.produto.preco
            atualizou = True
        if atualizou:
            self.save(update_fields=['nome_produto', 'preco_unitario'])
    def __str__(self):
        return f"{self.quantidade}x {self.nome_produto}"


# ============================================================
# PEDIDO
# ============================================================

class Pedido(models.Model):
    STATUS = [
        ('pendente_pagamento', 'Aguardando Pagamento'),
        ('pago', 'Pago'),
        ('em_preparacao', 'Aguardando Envio'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
        ('falha_pagamento', 'Falha no Pagamento'),
    ]
    METODOS_PAGAMENTO = [
        ('pix', 'Pix'),
        ('cartao_debito', 'Cartão de Débito'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('boleto', 'Boleto Bancário'),
    ]

    # ── Relacionamentos ──
    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.PROTECT,   # não deixa deletar usuário com pedido
        related_name='pedidos',
    )
    carrinho_origem = models.ForeignKey(
        Carrinho,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pedidos_gerados',
    )

    # ── Status e pagamento ──
    status = models.CharField(max_length=20, choices=STATUS, default='pendente_pagamento')
    metodo_pagamento = models.CharField(
        max_length=20, choices=METODOS_PAGAMENTO, null=True, blank=True
    )
    # Campos preenchidos pelo gateway (futuro). Vazios por enquanto.
    id_transacao_gateway = models.CharField(
        max_length=120, null=True, blank=True, unique=False
    )
    bandeira = models.CharField(max_length=30, null=True, blank=True)

    # ── Valores (congelados no momento da compra) ──
    valor_produtos = models.DecimalField(max_digits=10, decimal_places=2)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    # ── Frete (info do serviço escolhido) ──
    frete_transportadora = models.CharField(max_length=80, null=True, blank=True)
    frete_prazo_dias = models.PositiveSmallIntegerField(null=True, blank=True)

    # ── Endereço de entrega (CÓPIA, não FK. PARA IMPEDIR ALTERAÇÕES, DEPOIS DEVE HAVER UMA BRECHA MAS AINDA FALTA LOGICA) ──
    entrega_apelido = models.CharField(max_length=255, blank=True, null=True)
    entrega_cep = models.CharField(max_length=9)
    entrega_endereco = models.CharField(max_length=255)
    entrega_numero = models.CharField(max_length=20)
    entrega_complemento = models.CharField(max_length=100, blank=True, null=True)
    entrega_bairro = models.CharField(max_length=100)
    entrega_cidade = models.CharField(max_length=100)
    entrega_estado = models.CharField(max_length=2)

    # ── Datas ──
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    expira_em = models.DateTimeField(null=True, blank=True)
    pago_em = models.DateTimeField(null=True, blank=True)
    enviado_em = models.DateTimeField(null=True, blank=True)
    entregue_em = models.DateTimeField(null=True, blank=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', '-criado_em']),
            models.Index(fields=['status', 'expira_em']),
        ]
    def __str__(self):
        return f"Pedido #{self.pk} — {self.usuario.email} ({self.get_status_display()})"

    # ── Propriedades de conveniência (template não precisa saber lógica) ──
    @property
    def pode_avancar(self):
        return self.status in ('pendente_pagamento', 'pago', 'em_preparacao', 'enviado')
    @property
    def pendente(self):
        return self.status == 'pendente_pagamento'
    @property
    def expirado(self):
        if not self.expira_em or self.status != 'pendente_pagamento':
            return False
        return timezone.now() > self.expira_em
    @property
    def chat_disponivel(self):
        """Chat fica disponível depois do pagamento. WIP por enquanto."""
        return self.status in ('pago', 'em_preparacao', 'enviado', 'entregue')

    # ── Transições de estado ──
    # Sempre via método, nunca via .status = X. Isso evita estado
    # inconsistente (ex: pedido 'entregue' que voltou pra 'pendente').
    def marcar_como_pago(self, id_transacao=None, bandeira=None):
        """Chamado pelo gateway (futuro) ou pela view de simulação (dev).

        Valida que o pedido está em 'pendente_pagamento' antes de ir
        pra 'pago'. Se já estiver pago, levanta erro — sinaliza que
        o webhook chegou duplicado.
        """
        if self.status != 'pendente_pagamento':
            raise ValueError(
                f"Não dá pra marcar como pago um pedido em '{self.status}'."
            )
        self.status = 'pago'
        self.pago_em = timezone.now()
        if id_transacao:
            self.id_transacao_gateway = id_transacao
        if bandeira:
            self.bandeira = bandeira
        self.save(update_fields=[
            'status', 'pago_em', 'id_transacao_gateway', 'bandeira', 'atualizado_em'
        ])
    def marcar_como_em_preparacao(self):
        if self.status != 'pago':
            raise ValueError(
                f"Só dá pra preparar pedido pago. Esse está em '{self.status}'."
            )
        self.status = 'em_preparacao'
        self.save(update_fields=['status', 'atualizado_em'])

    def marcar_como_enviado(self, transportadora=None, prazo_dias=None):
        if self.status != 'em_preparacao':
            raise ValueError(
                f"Só dá pra enviar pedido em preparação. Esse está em '{self.status}'."
            )
        self.status = 'enviado'
        self.enviado_em = timezone.now()
        if transportadora:
            self.frete_transportadora = transportadora
        if prazo_dias is not None:
            self.frete_prazo_dias = prazo_dias
        self.save(update_fields=[
            'status', 'enviado_em', 'frete_transportadora',
            'frete_prazo_dias', 'atualizado_em'
        ])
    def marcar_como_entregue(self):
        if self.status != 'enviado':
            raise ValueError(
                f"Só dá pra entregar pedido enviado. Esse está em '{self.status}'."
            )
        self.status = 'entregue'
        self.entregue_em = timezone.now()
        self.save(update_fields=['status', 'entregue_em', 'atualizado_em'])
    def cancelar(self, motivo_terminal='cancelado'):
        if self.status in ('cancelado', 'falha_pagamento'):
            return  # já está num estado terminal, idempotente
        if self.status == 'entregue':
            raise ValueError("Pedido entregue não pode ser cancelado (só reembolsado).")
        # Devolve estoque de cada item. Ignora itens cujo produto foi deletado (não tem pra onde devolver).
        for item in self.itens.select_related('produto'):
            if item.produto is not None:
                item.produto.quantidade += item.quantidade
                item.produto.save(update_fields=['quantidade'])
        self.status = motivo_terminal
        self.cancelado_em = timezone.now()
        self.save(update_fields=['status', 'cancelado_em', 'atualizado_em'])
    def cancelar_por_expiracao(self):
        """Atalho pra cancelar pedidos pendentes que passaram do prazo."""
        if not self.expirado:
            return False
        self.cancelar(motivo_terminal='cancelado')
        return True
    # ── Helpers ──
    @classmethod
    def cancelar_pedidos_expirados(cls):
        agora = timezone.now()
        expirados = cls.objects.filter(
            status='pendente_pagamento',
            expira_em__lt=agora,
        )
        cancelados = []
        for pedido in expirados:
            pedido.cancelar(motivo_terminal='cancelado')
            cancelados.append(pedido)
        return cancelados


class ItemPedido(models.Model):
    # Item Snapshot basicamente
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
    )
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='itens_pedido',
    )
    # Snapshot — cópia congelada do estado do produto no momento da compra
    nome_produto = models.CharField(max_length=255)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    imagem_url = models.URLField(max_length=500, blank=True, null=True)
    quantidade = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        ordering = ['id']
    def save(self, *args, **kwargs):
        # Calcula subtotal automaticamente se não veio preenchido.
        # Isso evita erro de digitação em views.
        if self.subtotal is None:
            self.subtotal = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.quantidade}x {self.nome_produto} (Pedido #{self.pedido_id})"