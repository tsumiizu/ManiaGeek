from django.contrib import admin
from .models import *

admin.site.register(Produto)
admin.site.register(Categoria)
admin.site.register(Imagem)
admin.site.register(Anuncio)
admin.site.register(Pedido)
admin.site.register(AvaliacaoLoja)
admin.site.register(AvaliacaoServico)
admin.site.register(AvaliacaoProduto)