from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ProdutoForm, CategoriaForm
from django.db.models import Prefetch

def quatro_view(request): # Apenas para testes
    return render(request, '404.html')

def home_view(request): 
    categorias = Categoria.objects.prefetch_related('produto').all().order_by('nome')
    produtos = Produto.objects.all().order_by('-id')
    produtos_destaque= Produto.objects.filter(destaque=True)[:5]
    
    return render(request, 'home.html', {'produtos': produtos, 'produtos_destaque': produtos_destaque, 'categorias': categorias})


def detalhe_produto(request, id):
  
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'detalhe_produto.html', {'produto': produto})

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

def produtos_view(request):

    return render(request, 'produtos.html')
