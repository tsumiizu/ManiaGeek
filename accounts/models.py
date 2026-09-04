from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from cloudinary.models import CloudinaryField
# from cloudinary.utils import cloudinary_url

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
    # Da pra fazer a foto ser prefedefinida como gatinhos
    foto = CloudinaryField('image', folder='perfis/', null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def save(self, *args, **kwargs):
        if not self.pk and not self.foto:
            self.foto = get_random_avatar()
        elif self.foto == 'perfis/default05':
            self.foto = get_random_avatar()   
        super().save(*args, **kwargs)

