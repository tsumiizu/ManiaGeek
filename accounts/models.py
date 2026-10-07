from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
from cloudinary.models import CloudinaryField
import cloudinary.uploader
from datetime import timedelta

class CodigoVerificacao(models.Model):
    TIPO_CHOICES = [
        ('cadastro', 'Verificação de Cadastro'),
        ('login', 'Verificação de Login (2FA)'),
    ]
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='codigos_verificacao',
    )
    codigo = models.CharField(max_length=6)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    tentativas = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['-criado_em']
    @classmethod
    def gerar(cls, usuario, tipo):
        cls.objects.filter(usuario=usuario, tipo=tipo, usado=False).update(usado=True)
        codigo = f"{random.randint(0, 999999):06d}"
        return cls.objects.create(usuario=usuario, codigo=codigo, tipo=tipo)
    def expirado(self):
        return timezone.now() > self.criado_em + timedelta(minutes=10)
    def valido(self):
        return not self.usado and not self.expirado() and self.tentativas < 5

class DispositivoConfiavel(models.Model):
    # O token é viável porque mesmo se vazado ainda é necessário ter a senha
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='dispositivos_confiaveis',
    )
    token = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    def valido(self):
        return timezone.now() < self.expira_em

DEFAULT_AVATARS = [
    'default01',
    'default02',
    'default03',
    'default04',
    'default05',
    'default06',
    'default07',
    'default08',
    'default09',
    'default10',
    'default11',
    'default12',
    'default13',
    'default14',
    'default15',
    'default16',
    'default17',
    'default18',
    'default19',
    'default20',
    'default21',
]
def get_random_avatar():
    return random.choice(DEFAULT_AVATARS)

def nome_random():
    # Inserir nomes de gatos:
    adjetivos = ['Anônimo', 'Veloz', 'Sábio', 'Místico', 'Radiante', 'Gamer', 'Viajante', 'Explorador']
    nome_base = f"{random.choice(adjetivos)}{random.randint(100, 9999)}"
    while Usuario.objects.filter(display_name=nome_base).exists():
        nome_base = f"{random.choice(adjetivos)}{random.randint(100, 9999)}"
    return nome_base

class Usuario(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    display_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    foto = CloudinaryField('image', folder='perfis/', null=True, blank=True)
    limite_alteracao = models.PositiveSmallIntegerField(default=0)
    ultima_foto = models.DateField(null=True, blank=True)
    TROCAS_MENSAIS = 3
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def reseta_novo_mes(self):
        """Retorna True se resetou (precisa ser salvo)."""
        hoje = timezone.now().date()
        if not self.ultima_foto or (
            self.ultima_foto.month != hoje.month or
            self.ultima_foto.year != hoje.year
        ):
            self.limite_alteracao = 0
            # Não seta ultima_foto aqui: só ao registrar troca de fato.
            # Assim, se nunca trocou, fica None e reseta sempre que precisar.
            return True
        return False

    def pode_alterar(self):
        self.reseta_novo_mes()
        return self.limite_alteracao < self.TROCAS_MENSAIS

    def registrar_troca_foto(self):
        self.reseta_novo_mes()
        self.limite_alteracao += 1
        self.ultima_foto = timezone.now().date()

    def deletar_cloudinary(self, foto_antiga):
        if not foto_antiga:
            return False
        public_id = getattr(foto_antiga, 'public_id', None)
        if not public_id:
            public_id = str(foto_antiga)
            if '/upload/' in public_id:
                try:
                    path = public_id.split('/upload/', 1)[1]
                    if path.startswith('v') and '/' in path:
                        path = path.split('/', 1)[1]
                    public_id = path.rsplit('.', 1)[0]
                except (IndexError, ValueError):
                    return False
        if not public_id:
            return False
        if any(avatar in public_id for avatar in DEFAULT_AVATARS):
            return False
        try:
            result = cloudinary.uploader.destroy(public_id, invalidate=True)
            return result.get('result') == 'ok'
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                "Falha ao deletar %s do Cloudinary: %s", public_id, e
            )
            return False
        
    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = nome_random()
        if not self.pk and not self.foto:
            self.foto = get_random_avatar()
        super().save(*args, **kwargs)

