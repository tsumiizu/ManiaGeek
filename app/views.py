from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group  
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.conf import settings
from decimal import Decimal
import cloudinary.uploader
from .models import *
from .forms import ProdutoForm, CategoriaForm, EnderecoForm 
from accounts.forms import EditarPerfilForm, UserRegisterForm, FotoPerfilForm, CodigoVerificacaoForm
from accounts.models import CodigoVerificacao, Usuario
from accounts.utils import (enviar_codigo_email, gerar_token_dispositivo, token_dispositivo_valido, ultimo_codigo_recente)


def quatro_view(request):  # Apenas para testes
    return render(request, '404.html')

def home_view(request):
    categorias = Categoria.objects.prefetch_related('produto').all().order_by('nome')
    produtos = Produto.objects.all().order_by('-id')
    produtos_destaque = Produto.objects.filter(destaque=True)[:5]

    return render(request, 'home.html', {
        'produtos': produtos,
        'produtos_destaque': produtos_destaque,
        'categorias': categorias,
    })


def detalhe_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    produtos_relacionados = Produto.objects.filter(
        produto_tipo=produto.produto_tipo
    ).exclude(id=id)[:4]

    return render(request, 'detalhe_produto.html', {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
    })
def produtos(request):
    produtos = Produto.objects.all()
    query = request.GET.get('q')
    tipo = request.GET.get('tipo')
    categoria = request.GET.get('categoria')
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


# ============================================================
# CARRINHO
# ============================================================

def carrinho_view(request):
    carrinho = Carrinho.obter_para_request(request)
    for item in carrinho.itens.all():
        item.sincronizar_com_produto()
    itens = carrinho.itens.select_related('produto').all()
    return render(request, 'carrinho.html', {
        'carrinho': carrinho,
        'itens': itens,
    })


@require_POST
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if produto.quantidade <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'erro': 'Produto sem estoque.'}, status=400)
        messages.error(request, "Produto sem estoque.")
        return redirect('detalhe_produto', id=produto_id)
    carrinho = Carrinho.obter_para_request(request)
    try:
        quantidade = int(request.POST.get('quantidade', 1))
    except (TypeError, ValueError):
        quantidade = 1
    quantidade = max(1, quantidade)
    with transaction.atomic():
        item, criado = ItemCarrinho.objects.select_for_update().get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={
                'nome_produto': produto.nome,
                'preco_unitario': produto.preco,
                'imagem_url': produto.imagem_capa,
                'quantidade': 0,
            },
        )
        nova_qtd = item.quantidade + quantidade
        if nova_qtd > produto.quantidade:
            nova_qtd = produto.quantidade
        item.quantidade = nova_qtd
        item.nome_produto = produto.nome
        item.preco_unitario = produto.preco
        item.imagem_url = produto.imagem_capa
        item.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'quantidade_carrinho': carrinho.quantidade_total,
            'subtotal_carrinho': str(carrinho.subtotal),
        })
    messages.success(request, f"{produto.nome} adicionado ao carrinho.")
    return redirect(request.POST.get('next') or 'carrinho')
@require_POST
def atualizar_quantidade(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id)
    carrinho = Carrinho.obter_para_request(request)
    if item.carrinho_id != carrinho.id:
        return JsonResponse({'ok': False, 'erro': 'Item não pertence a você.'}, status=403)
    try:
        nova_qtd = int(request.POST.get('quantidade', 1))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'erro': 'Quantidade inválida.'}, status=400)
    if nova_qtd < 1:
        return JsonResponse({'ok': False, 'erro': 'Quantidade mínima é 1.'}, status=400)
    if item.produto and nova_qtd > item.produto.quantidade:
        nova_qtd = item.produto.quantidade
    item.quantidade = nova_qtd
    item.save(update_fields=['quantidade'])
    return JsonResponse({
        'ok': True,
        'quantidade': item.quantidade,
        'subtotal_item': str(item.subtotal),
        'subtotal_carrinho': str(carrinho.subtotal),
        'quantidade_carrinho': carrinho.quantidade_total,
    })
@require_POST
def remover_do_carrinho(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id)
    carrinho = Carrinho.obter_para_request(request)
    if item.carrinho_id != carrinho.id:
        return JsonResponse({'ok': False, 'erro': 'Item não pertence a você.'}, status=403)

    item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'subtotal_carrinho': str(carrinho.subtotal),
            'quantidade_carrinho': carrinho.quantidade_total,
            'carrinho_vazio': not carrinho.itens.exists(),
        })
    messages.success(request, "Item removido do carrinho.")
    return redirect('carrinho')

# ============================================================
# PEDIDOS
# ============================================================
# ── Constantes do checkout (fictícias por enquanto) ──
FRETE_FIXO = Decimal('19.90')
FRETE_TRANSPORTADORA = 'Correios PAC (fictício)'
FRETE_PRAZO_DIAS = 7
PRAZO_PAGAMENTO_MINUTOS = 30


def _pode_ver_pedido(request, pedido):
    return (
        request.user.is_authenticated
        and (pedido.usuario_id == request.user.id or request.user.is_staff)
    )
@login_required
def checkout_view(request):
    carrinho = Carrinho.obter_para_request(request)
    # Carrinho vazio ou com item indisponível: não dá pra fechar.
    if not carrinho.pode_fechar:
        messages.error(
            request,
            "Seu carrinho está vazio ou tem itens indisponíveis. "
            "Resolva antes de finalizar a compra."
        )
        return redirect('carrinho')
    enderecos = request.user.enderecos.all()
    if not enderecos.exists():
        messages.warning(
            request,
            "Cadastre um endereço de entrega antes de finalizar a compra."
        )
        return redirect('endereco_adicionar')
    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        metodo = request.POST.get('metodo_pagamento')
        # ── Validações ──
        try:
            endereco = request.user.enderecos.get(id=endereco_id)
        except (Endereco.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Escolha um endereço válido.")
            return render(request, 'checkout.html', {
                'carrinho': carrinho, 'enderecos': enderecos,
            })
        metodos_validos = {m[0] for m in Pedido.METODOS_PAGAMENTO}
        if metodo not in metodos_validos:
            messages.error(request, "Escolha um método de pagamento.")
            return render(request, 'checkout.html', {
                'carrinho': carrinho, 'enderecos': enderecos,
            })
        # Reconfere estoque item a item (pode ter mudado desde o GET).
        for item in carrinho.itens.select_related('produto'):
            if item.produto is None:
                messages.error(request, f"'{item.nome_produto}' foi removido da loja.")
                return redirect('carrinho')
            if item.quantidade > item.produto.quantidade:
                messages.error(
                    request,
                    f"'{item.produto.nome}' só tem {item.produto.quantidade} em estoque. "
                    "Ajuste a quantidade no carrinho."
                )
                return redirect('carrinho')
        # ── Criação do pedido (tudo ou nada) ──
        with transaction.atomic():
            valor_produtos = carrinho.subtotal
            valor_total = valor_produtos + FRETE_FIXO
            pedido = Pedido.objects.create(
                usuario=request.user,
                carrinho_origem=carrinho,
                status='pendente_pagamento',
                metodo_pagamento=metodo,
                valor_produtos=valor_produtos,
                valor_frete=FRETE_FIXO,
                valor_total=valor_total,
                frete_transportadora=FRETE_TRANSPORTADORA,
                frete_prazo_dias=FRETE_PRAZO_DIAS,
                # Endereço: CÓPIA dos campos. Se o usuário editar depois,
                # esse pedido continua com o endereço original.
                entrega_apelido=endereco.apelido,
                entrega_cep=endereco.cep or '',
                entrega_endereco=endereco.endereco or '',
                entrega_numero=endereco.numero or '',
                entrega_complemento=endereco.complemento,
                entrega_bairro=endereco.bairro or '',
                entrega_cidade=endereco.cidade or '',
                entrega_estado=endereco.estado or '',
                expira_em=timezone.now() + timezone.timedelta(minutes=PRAZO_PAGAMENTO_MINUTOS),
            )
            # Congela os itens e decrementa o estoque no mesmo passo.
            for item in carrinho.itens.select_related('produto'):
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item.produto,
                    nome_produto=item.nome_produto,
                    preco_unitario=item.preco_unitario,
                    imagem_url=item.imagem_url,
                    quantidade=item.quantidade,
                    subtotal=item.subtotal,
                )
                # Decrementa estoque. É o "reserva" mais simples que existe. Se o pedido for cancelado depois, o estoque volta no Pedido.cancelar().
                item.produto.quantidade -= item.quantidade
                item.produto.save(update_fields=['quantidade'])
            # Marca o carrinho como convertido. NÃO deleta — histórico.
            carrinho.status = 'convertido'
            carrinho.save(update_fields=['status'])
        messages.success(request, f"Pedido #{pedido.id} criado! Falta pagar.")
        return redirect('pedido_detalhe', pk=pedido.id)
    return render(request, 'checkout.html', {
        'carrinho': carrinho,
        'enderecos': enderecos,
        'metodos_pagamento': Pedido.METODOS_PAGAMENTO,
        'frete': FRETE_FIXO,
        'frete_transportadora': FRETE_TRANSPORTADORA,
        'frete_prazo_dias': FRETE_PRAZO_DIAS,
    })

@login_required
def pedido_detalhe_view(request, pk):
    Pedido.cancelar_pedidos_expirados()  # limpa pendentes vencidos
    pedido = get_object_or_404(Pedido, pk=pk)
    if not _pode_ver_pedido(request, pedido):
        # 404 em vez de 403: não vaza a existência do pedido.
        from django.http import Http404
        raise Http404
    return render(request, 'detalhe_pedido.html', {
        'pedido': pedido,
        'itens': pedido.itens.select_related('produto').all(),
        # DEBUG=True habilita os botões dev no template.
        'modo_dev': settings.DEBUG,
    })

@login_required
def pedido_lista_view(request):
    Pedido.cancelar_pedidos_expirados()
    pedidos = request.user.pedidos.prefetch_related('itens').all()
    return render(request, 'lista_pedido.html', {
        'pedidos': pedidos,
    })

@login_required
@require_POST
def pedido_simular_pagamento_view(request, pk):
    """Botão DEV: simula o pagamento aprovado.

    Em produção, quem chama Pedido.marcar_como_pago() é o webhook do
    gateway. Aqui chamamos direto, só pra testar. Protegido por
    settings.DEBUG pra não existir em produção.
    """
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404
    pedido = get_object_or_404(Pedido, pk=pk)
    if not _pode_ver_pedido(request, pedido):
        from django.http import Http404
        raise Http404
    try:
        pedido.marcar_como_pago(
            id_transacao=f"DEV-{timezone.now().timestamp():.0f}",
            bandeira='DEV',
        )
        messages.success(request, "Pagamento simulado! Pedido marcado como pago.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('pedido_detalhe', pk=pedido.id)

@login_required
@require_POST
def pedido_avancar_view(request, pk):
    """Botão DEV: avança o pedido pro próximo estado lógico.

    Mapeamento:
      pago           → em_preparacao
      em_preparacao  → enviado
      enviado        → entregue
      pendente       → não avança (precisa simular pagamento antes)

    Em produção, essas transições vêm do painel do vendedor. Aqui é
    só pra testar o fluxo. Protegido por settings.DEBUG.
    """
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404
    pedido = get_object_or_404(Pedido, pk=pk)
    if not _pode_ver_pedido(request, pedido):
        from django.http import Http404
        raise Http404
    try:
        if pedido.status == 'pago':
            pedido.marcar_como_em_preparacao()
            messages.success(request, "Pedido em preparação.")
        elif pedido.status == 'em_preparacao':
            pedido.marcar_como_enviado(
                transportadora=pedido.frete_transportadora or FRETE_TRANSPORTADORA,
                prazo_dias=pedido.frete_prazo_dias or FRETE_PRAZO_DIAS,
            )
            messages.success(request, "Pedido enviado.")
        elif pedido.status == 'enviado':
            pedido.marcar_como_entregue()
            messages.success(request, "Pedido entregue!")
        elif pedido.status == 'pendente_pagamento':
            messages.error(
                request,
                "Pedido ainda pendente. Use 'Simular pagamento' primeiro."
            )
        else:
            messages.error(request, "Pedido já está num estado terminal.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('pedido_detalhe', pk=pedido.id)

# ============================================================
# PERFIL
# ============================================================

@login_required
def perfil_view(request):
    perfil_form = EditarPerfilForm(instance=request.user)
    foto_form = FotoPerfilForm(instance=request.user)
    if request.method == 'POST':
        if 'foto' in request.FILES:
            foto_form = FotoPerfilForm(request.POST, request.FILES, instance=request.user)
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

# ENDEREÇOS

@login_required
def endereco_adicionar(request):
    LIMITE = 5
    if request.user.enderecos.count() >= LIMITE:
        messages.error(
            request,
            f"Você já tem {LIMITE} endereços cadastrados. "
            "Remova um antes de adicionar outro."
        )
        return redirect('perfil')
    if request.method == 'POST':
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            endereco.user = request.user
            endereco.save()
            messages.success(request, "Endereço adicionado com sucesso!")
            return redirect('perfil')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = EnderecoForm()
    return render(request, 'endereco_form.html', {
        'form': form,
        'titulo': 'Novo Endereço',
    })
@login_required
def endereco_editar(request, pk):
    endereco = get_object_or_404(Endereco, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EnderecoForm(request.POST, instance=endereco)
        if form.is_valid():
            form.save()
            messages.success(request, "Endereço atualizado!")
            return redirect('perfil')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = EnderecoForm(instance=endereco)

    return render(request, 'endereco_form.html', {
        'form': form,
        'titulo': 'Editar Endereço',
        'endereco': endereco,
    })
@login_required
@require_POST
def endereco_remover(request, pk):
    endereco = get_object_or_404(Endereco, pk=pk, user=request.user)
    endereco.delete()
    messages.success(request, "Endereço removido.")
    return redirect('perfil')

# ============================================================
# CADASTRO / LOGIN / 2FA
# ============================================================

def cadastro_view(request):
    # VERSÃO TEMPORÁRIA: cadastro sem verificação por e-mail.
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # ← MERGE (cadastro): captura o carrinho anônimo ANTES de logar.
            carrinho_anonimo = None
            if request.session.session_key:
                carrinho_anonimo = Carrinho.objects.filter(
                    session_key=request.session.session_key,
                    status='ativo',
                ).first()
            login(request, usuario)
            # ← MERGE (cadastro): agora que logou, migra o carrinho.
            if carrinho_anonimo:
                carrinho_anonimo.migrar_para_usuario(usuario)
            messages.success(
                request,
                f'Conta criada com sucesso! Bem-vindo, {usuario.display_name}!'
            )
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/cadastro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        senha = request.POST.get('password', '')
        usuario = authenticate(request, username=email, password=senha)
        if usuario is None:
            messages.error(request, "E-mail ou senha incorretos.")
        elif not usuario.is_active:
            messages.error(request, "Conta não verificada. Finalize o cadastro.")
            return redirect('cadastro')
        else:
            token = request.COOKIES.get('dispositivo_confiavel')
            disp = token_dispositivo_valido(token)
            # Caminho rápido: dispositivo confiável, pula 2FA.
            if disp and disp.usuario_id == usuario.id:
                # ← MERGE (login c/ dispositivo confiável): captura antes.
                carrinho_anonimo = None
                if request.session.session_key:
                    carrinho_anonimo = Carrinho.objects.filter(
                        session_key=request.session.session_key,
                        status='ativo',
                    ).first()
                login(request, usuario)
                # ← MERGE: migra depois.
                if carrinho_anonimo:
                    carrinho_anonimo.migrar_para_usuario(usuario)
                messages.success(request, f"Bem-vindo de volta, {usuario.display_name}!")
                return redirect('home')
            # Caminho normal: gera código de 2FA e redireciona pra verificação.
            codigo = CodigoVerificacao.gerar(usuario, 'login')
            try:
                enviar_codigo_email(usuario, codigo.codigo, 'login')
            except Exception:
                messages.error(request, "Não conseguimos enviar o código. Tente novamente.")
                return render(request, 'login.html')
            request.session['2fa_usuario_id'] = usuario.id
            request.session['2fa_lembrar'] = 'remember' in request.POST
            messages.success(request, "Enviamos um código para o seu e-mail.")
            return redirect('verificar_login')
    return render(request, 'registration/login.html')
def verificar_login_view(request):
    usuario_id = request.session.get('2fa_usuario_id')
    if not usuario_id:
        messages.error(request, "Sessão expirada. Faça login novamente.")
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = CodigoVerificacaoForm(request.POST)
        if form.is_valid():
            codigo_digitado = form.cleaned_data['codigo']
            registro = CodigoVerificacao.objects.filter(
                usuario=usuario, tipo='login', usado=False
            ).first()

            if not registro or not registro.valido():
                messages.error(request, "Código expirado ou inválido. Peça um novo.")
                return render(request, 'registration/verificar.html', {'form': form})

            if registro.codigo != codigo_digitado:
                registro.tentativas += 1
                registro.save(update_fields=['tentativas'])
                restantes = 5 - registro.tentativas
                messages.error(request, f"Código incorreto. Tentativas restantes: {restantes}.")
                return render(request, 'registration/verificar.html', {'form': form})
            # Sucesso no 2FA
            registro.usado = True
            registro.save(update_fields=['usado'])
            lembrar = request.session.pop('2fa_lembrar', False)
            request.session.pop('2fa_usuario_id', None)
            # ← MERGE (2FA): captura o carrinho anônimo ANTES do login().
            carrinho_anonimo = None
            if request.session.session_key:
                carrinho_anonimo = Carrinho.objects.filter(
                    session_key=request.session.session_key,
                    status='ativo',
                ).first()
            login(request, usuario)
            # ← MERGE (2FA): migra depois.
            if carrinho_anonimo:
                carrinho_anonimo.migrar_para_usuario(usuario)

            response = redirect('home')
            if lembrar:
                disp = gerar_token_dispositivo(usuario)
                response.set_cookie(
                    'dispositivo_confiavel',
                    disp.token,
                    max_age=60 * 60 * 24 * 30,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                )
            if not lembrar:
                request.session.set_expiry(0)

            messages.success(request, f"Bem-vindo de volta, {usuario.display_name}!")
            return response
    else:
        form = CodigoVerificacaoForm()

    return render(request, 'registration/verificar.html', {
        'form': form,
        'email': usuario.email,
    })
def reenviar_codigo_login_view(request):
    usuario_id = request.session.get('2fa_usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if ultimo_codigo_recente(usuario, 'login', segundos=60):
        messages.error(request, "Aguarde 1 minuto para pedir um novo código.")
        return redirect('verificar_login')
    codigo = CodigoVerificacao.gerar(usuario, 'login')
    try:
        enviar_codigo_email(usuario, codigo.codigo, 'login')
        messages.success(request, "Novo código enviado.")
    except Exception:
        messages.error(request, "Falha ao enviar. Tente novamente.")
    return redirect('verificar_login')

# ============================================================
# DASHBOARD (STAFF)
# ============================================================

# (PERMISSÕES)
def _acessa_dashboard(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.exists()
def _gerencia_usuarios(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='Dono').exists()
def _gerencia_produtos(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(
        name__in=['Dono', 'Gestor de Produtos']
    ).exists()
def _gerencia_pedidos(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(
        name__in=['Dono', 'Gestor de Pedidos', 'Suporte']
    ).exists()
@user_passes_test(_acessa_dashboard, login_url='login')
def dashboard_view(request):
    total_usuarios = Usuario.objects.count()
    total_produtos = Produto.objects.count()
    total_categorias = Categoria.objects.count()
    pedidos_abertos = Pedido.objects.filter(
        status__in=['pendente_pagamento', 'pago', 'em_preparacao', 'enviado']
    ).count()
    pedidos_totais = Pedido.objects.count()
    pode_ver_usuarios = _gerencia_usuarios(request.user)
    pode_ver_pedidos = _gerencia_pedidos(request.user)
    pendencias = []
    if pode_ver_pedidos:
        pendencias = Pedido.objects.select_related('usuario').filter(status__in=['pendente_pagamento', 'pago', 'em_preparacao', 'enviado']).order_by('-criado_em')[:10]
    return render(request, 'administrador/dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_produtos': total_produtos,
        'total_categorias': total_categorias,
        'pedidos_abertos': pedidos_abertos,
        'pedidos_totais': pedidos_totais,
        'pendencias': pendencias,
        'pode_ver_usuarios': pode_ver_usuarios,
        'pode_ver_pedidos': pode_ver_pedidos,
    })

@user_passes_test(_gerencia_usuarios, login_url='login')
def dashboard_usuarios_view(request):
    usuarios = Usuario.objects.all().order_by('-date_joined')
    q = request.GET.get('q', '').strip()
    if q:
        usuarios = usuarios.filter(
            models.Q(email__icontains=q) |
            models.Q(display_name__icontains=q) |
            models.Q(username__icontains=q)
        )
    usuarios = usuarios.prefetch_related('groups')
    todos_grupos = Group.objects.all().order_by('name')
    eh_superuser = request.user.is_superuser
    eh_dono = request.user.groups.filter(name='Dono').exists()
    pode_gerenciar_cargos = eh_superuser or eh_dono
    for u in usuarios:
        # - Superuser logado: vê o badge "Superuser" na PRÓPRIA linha e nos OUTROS superusers também (ele já sabe quem é, não vaza nada pra ele).
        # - Dono não-superuser: NÃO vê badge em nenhum superuser.
        u.eh_superuser_visivel = u.is_superuser and eh_superuser
        if not pode_gerenciar_cargos:
            u.pode_editar_cargo = False
        elif u.id == request.user.id:
            u.pode_editar_cargo = False
        else:
            u.pode_editar_cargo = True
    return render(request, 'administrador/dashboard_usuarios.html', {
        'usuarios': usuarios,
        'q': q,
        'todos_grupos': todos_grupos,
        'pode_gerenciar_cargos': pode_gerenciar_cargos,
    })
@user_passes_test(_gerencia_usuarios, login_url='login')
@require_POST
def user_trocar_grupo_view(request, usuario_id):
    usuario_alvo = get_object_or_404(Usuario, id=usuario_id)
    if usuario_alvo.id == request.user.id:
        return JsonResponse(
            {'ok': False, 'erro': 'Você não pode alterar seus próprios grupos.'},
            status=400,
        )
    if usuario_alvo.is_superuser:
        if request.user.is_superuser:
            return JsonResponse(
                {'ok': False, 'erro': 'Não é possível alterar grupos de outro superuser.'},
                status=400,
            )
        return JsonResponse({
            'ok': True,
            'usuario_id': usuario_alvo.id,
            'grupos': [
                {'id': g.id, 'nome': g.name}
                for g in usuario_alvo.groups.all()
            ],
        })
    eh_dono = request.user.groups.filter(name='Dono').exists()
    if not eh_dono and not request.user.is_superuser:
        return JsonResponse(
            {'ok': False, 'erro': 'Apenas o Dono ou superuser pode alterar cargos.'},
            status=403,
        )
    grupos_ids = [gid for gid in request.POST.getlist('grupos_ids') if gid.strip()]
    grupos = Group.objects.filter(id__in=grupos_ids)
    usuario_alvo.groups.set(grupos)
    return JsonResponse({
        'ok': True,
        'usuario_id': usuario_alvo.id,
        'grupos': [{'id': g.id, 'nome': g.name} for g in usuario_alvo.groups.all()],
    })

@user_passes_test(_gerencia_pedidos, login_url='login')
def dashboard_pedidos_view(request):
    """Lista TODOS os pedidos (não só do usuário logado). Só staff."""
    Pedido.cancelar_pedidos_expirados()
    pedidos = Pedido.objects.select_related('usuario').order_by('-criado_em')

    # Filtro por status (opcional, via querystring)
    status_filtro = request.GET.get('status', '').strip()
    if status_filtro and status_filtro in dict(Pedido.STATUS):
        pedidos = pedidos.filter(status=status_filtro)

    return render(request, 'administrador/dashboard_pedidos.html', {
        'pedidos': pedidos,
        'status_filtro': status_filtro,
        'status_choices': Pedido.STATUS,
    })

@user_passes_test(_gerencia_produtos, login_url='login')
def produto_criar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            for i in range(1, 4):
                imagem = request.FILES.get(f'img_slot_{i}_imagem')
                alt = request.POST.get(f'img_slot_{i}_alt', '').strip()
                if imagem:
                    Imagem.objects.create(
                        produto=produto,
                        imagem=imagem,
                        alt_text=alt or produto.nome,
                    )
            messages.success(request, f"Produto '{produto.nome}' cadastrado!")
            return redirect('produtos')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = ProdutoForm()
    slots_imagens = [
        {'indice': 1, 'imagem': None},
        {'indice': 2, 'imagem': None},
        {'indice': 3, 'imagem': None},
    ]
    return render(request, 'administrador/produto_form.html', {
        'form': form,
        'titulo': 'Novo Produto',
        'slots_imagens': slots_imagens,
    })
@user_passes_test(_gerencia_produtos, login_url='login')
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    imagens_qs = list(produto.Imagem.all().order_by('id'))
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            produto = form.save()
            for i in range(1, 4):
                imagem = request.FILES.get(f'img_slot_{i}_imagem')
                alt = request.POST.get(f'img_slot_{i}_alt', '').strip()
                remover = request.POST.get(f'img_slot_{i}_remover') == '1'
                imagem_atual = imagens_qs[i - 1] if i <= len(imagens_qs) else None
                if remover and imagem_atual:
                    imagem_atual.delete()
                elif imagem and imagem_atual:
                    try:
                        cloudinary.uploader.destroy(
                            imagem_atual.imagem.public_id, invalidate=True
                        )
                    except Exception:
                        pass
                    imagem_atual.imagem = imagem
                    imagem_atual.alt_text = alt or produto.nome
                    imagem_atual.save()
                elif imagem and not imagem_atual:
                    Imagem.objects.create(
                        produto=produto,
                        imagem=imagem,
                        alt_text=alt or produto.nome,
                    )
                elif imagem_atual and alt:
                    imagem_atual.alt_text = alt
                    imagem_atual.save(update_fields=['alt_text'])
            messages.success(request, f"Produto '{produto.nome}' atualizado!")
            return redirect('produtos')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = ProdutoForm(instance=produto)
    imagens_qs = list(produto.Imagem.all().order_by('id'))
    slots_imagens = []
    for i in range(3):
        if i < len(imagens_qs):
            slots_imagens.append({'indice': i + 1, 'imagem': imagens_qs[i]})
        else:
            slots_imagens.append({'indice': i + 1, 'imagem': None})
    return render(request, 'administrador/produto_form.html', {
        'form': form,
        'titulo': 'Editar Produto',
        'slots_imagens': slots_imagens,
    })
@user_passes_test(_gerencia_produtos, login_url='login')
def categoria_criar(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoriaForm()
    return render(request, 'administrador/categoria_form.html', {
        'form': form,
        'titulo': 'Nova Categoria',
        'todas_categorias': Categoria.objects.all().order_by('nome'),
    })
@user_passes_test(_gerencia_produtos, login_url='login')
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'administrador/categoria_form.html', {
        'form': form,
        'titulo': 'Editar Categoria',
        'categoria': categoria,
        'todas_categorias': Categoria.objects.all().order_by('nome'),
    })