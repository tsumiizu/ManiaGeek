from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ProdutoForm, CategoriaForm

def home_view(request):
    slides = Anuncio.objects.all()[:3] 
    produtos_destaque = Produto.objects.all()[:6]
    for produto in produtos_destaque:
        imagem_capa = produto.Imagem.filter(capa=True).first()
        if imagem_capa and imagem_capa.imagem:
            produto.url_capa = imagem_capa.imagem.url
            produto.alt_capa = imagem_capa.alt_text
        else:
            produto.url_capa = '' 
            produto.alt_capa = produto.nome
        categoria = produto.categoria.first()
        produto.nome_categoria = categoria.nome if categoria else produto.get_produto_tipo_display()
    context = {
        'slides': slides,
        'produtos_destaque': produtos_destaque,
    }
    return render(request, 'home.html', context)    

def produtos_view(request):
    return render(request, 'produtos.html')


# Administrador 

def produto_criar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm() 
    return render(request, 'produto_form.html', {'form': form, 'titulo': 'Novo Produto'})

def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto) 
    return render(request, 'produto_form.html', {'form': form, 'titulo': 'Editar Produto'})

def categoria_criar(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('')
    else:
        form = CategoriaForm() 
    return render(request, '.html', {'form': form, 'titulo': 'Novo Categoria'})

def categoria_editar(request, pk):
    produto = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=Categoria)
        if form.is_valid():
            form.save()
            return redirect('')
    else:
        form = CategoriaForm(instance=Categoria) 
    return render(request, '.html', {'form': form, 'titulo': 'Editar Categoria'})