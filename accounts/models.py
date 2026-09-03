from django.contrib.auth.models import AbstractUser
from django.db import models
import random
# from cloudinary.models import CloudinaryField
# from cloudinary.utils import cloudinary_url

# DEFAULT_AVATARS = [
#     'avatar_default01',
#     'avatar_default02',
#     'avatar_default03',
#     'avatar_default04',
#     'avatar_default05',
#     'avatar_default06',
#     'avatar_default07',
# ]
# def get_random_avatar():
#     return random.choice(DEFAULT_AVATARS)

def nome_random():
    # Inserir nomes de gatos:
    adjetivos = ['Anônimo', 'Veloz', 'Sábio', 'Místico', 'Radiante', 'Gamer', 'Dev', 'Viajante', 'Membro', 'Explorador']
    nome_base = f"{random.choice(adjetivos)}{random.randint(100, 9999)}"
    while Usuario.objects.filter(display_name=nome_base).exists():
        nome_base = f"{random.choice(adjetivos)}{random.randint(100, 9999)}"
    return nome_base

class Usuario(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    display_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    # Da pra fazer a foto ser prefedefinida como gatinhos
    # foto = models.ImageField(upload_to='media/perfis/', blank=True, null=True)
    # foto = CloudinaryField('image', folder='perfis/', null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    # def save(self, *args, **kwargs):
    #     if not self.pk and not self.foto:
    #         self.foto = get_random_avatar()
    #     elif self.foto == 'perfis/default05':
    #         self.foto = get_random_avatar()   
    #     super().save(*args, **kwargs)
    # @property
    # def foto_url(self):
    #     if not self.foto:
    #         url, _ = cloudinary_url(get_random_avatar(), secure=True)
    #         return url
    #     if hasattr(self.foto, 'url') and self.foto.url:
    #         return self.foto.url
    #     foto_str = str(self.foto)
    #     if foto_str == 'perfis/default05':
    #         url, _ = cloudinary_url(get_random_avatar(), secure=True)
    #         return url
    #     url, _ = cloudinary_url(foto_str, secure=True)
    #     return url
