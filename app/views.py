from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ProdutoForm, CategoriaForm
from accounts.forms import EditarPerfilForm, UserRegisterForm, FotoPerfilForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def quatro_view(request): # Apenas para testes
    return render(request, '404.html')

def home_view(request): 
    categorias = Categoria.objects.prefetch_related('produto').all().order_by('nome')
    produtos = Produto.objects.all().order_by('-id')
    produtos_destaque= Produto.objects.filter(destaque=True)[:5]
    
    return render(request, 'home.html', {'produtos': produtos, 'produtos_destaque': produtos_destaque, 'categorias': categorias})

def detalhe_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    
    produtos_relacionados = Produto.objects.filter(
        produto_tipo=produto.produto_tipo
    ).exclude(id=id)[:4]
    
    return render(request, 'detalhe_produto.html', {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados
    })

def produtos(request):
    produtos = Produto.objects.all()
    
    # Pega os parâmetros da URL
    query = request.GET.get('q')
    tipo = request.GET.get('tipo')
    categoria = request.GET.get('categoria') 
    # Filtros
    if query:
        produtos = produtos.filter(nome__icontains=query)
    if tipo:
        produtos = produtos.filter(produto_tipo=tipo)
    if categoria:

        produtos = produtos.filter(categoria__nome__iexact=categoria)

    return render(request, 'produtos.html', {
        'produtos': produtos,
        'query': query,
    })

def carrinho(request):
    return render(request, 'carrinho.html')

# User related

@login_required
def perfil_view(request):
    perfil_form = EditarPerfilForm(instance=request.user)
    foto_form = FotoPerfilForm(instance=request.user)
    if request.method == 'POST':
        if 'foto' in request.FILES:
            foto_form = FotoPerfilForm(
                request.POST, request.FILES, instance=request.user
            )
            if foto_form.is_valid():
                foto_form.save()
                messages.success(request, "Foto atualizada!")
                return redirect('perfil')
            messages.error(request, "Não foi possível trocar a foto.")
        else:
            perfil_form = EditarPerfilForm(request.POST, instance=request.user)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, "Dados atualizados!")
                return redirect('perfil')
            messages.error(request, "Corrija os erros abaixo.")
    return render(request, 'perfil.html', {
        'form': perfil_form,
        'foto_form': foto_form,
    })

def cadastro_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'Conta criada com sucesso! Bem-vindo, {usuario.display_name}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/cadastro.html', {'form': form})

# Administrador 

def produto_criar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm() 
    return render(request, 'administrador/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})

def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto) 
    return render(request, 'administrador/produto_form.html', {'form': form, 'titulo': 'Editar Produto'})

def categoria_criar(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home') # Por enquanto home
    else:
        form = CategoriaForm() 
    return render(request, 'administrador/categoria_form.html', {'form': form, 'titulo': 'Nova Categoria'})

def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoriaForm(instance=categoria) 
    return render(request, 'administrador/categoria_form.html', {'form': form, 'titulo': 'Editar Categoria', 'categoria': categoria})