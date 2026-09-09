from django.shortcuts import render, render, get_object_or_404
from .models import Produto
from .models import Produto, Anuncio

# Create your views here.
def home_view(request):
    # Pega os últimos 3 anúncios para o carrossel
    slides = Anuncio.objects.all()[:3] 
    
    # Pega os últimos 6 produtos para a vitrine
    produtos_destaque = Produto.objects.all()[:6]

    # Vamos "injetar" a imagem de capa e a categoria principal em cada produto 
    # para facilitar a vida do nosso HTML
    for produto in produtos_destaque:
        # Busca a imagem marcada como capa usando o related_name 'Imagem'
        imagem_capa = produto.Imagem.filter(capa=True).first()
        
        if imagem_capa and imagem_capa.imagem:
            produto.url_capa = imagem_capa.imagem.url
            produto.alt_capa = imagem_capa.alt_text
        else:
            produto.url_capa = '' # Aqui você pode por o link de uma imagem padrão de "Sem foto"
            produto.alt_capa = produto.nome

        # Pega o nome da primeira categoria (se existir), senão usa o tipo do produto
        categoria = produto.categoria.first()
        produto.nome_categoria = categoria.nome if categoria else produto.get_produto_tipo_display()

    context = {
        'slides': slides,
        'produtos_destaque': produtos_destaque,
    }
    
    return render(request, 'home.html', context)  
 
def produtos_view(request):
    return render(request, 'produtos.html')
def detalhe_produto(request, id):

    produto = get_object_or_404(Produto, id=id)
    
    return render(request, 'detalhe_produto.html', {'produto': produto})