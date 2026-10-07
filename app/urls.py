from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home_view, name='home'),
    path('produto/', views.produtos, name='produtos'),
    path('produto/<int:id>/', views.detalhe_produto, name='detalhe_produto'),
    # Carrinho
    path('carrinho/', views.carrinho_view, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/item/<int:item_id>/quantidade/', views.atualizar_quantidade, name='atualizar_quantidade'),
    path('carrinho/item/<int:item_id>/remover/', views.remover_do_carrinho, name='remover_do_carrinho'),
    # Rotas de pedido — Misturadas com as de dev depois apague as de dev
    path('checkout/', views.checkout_view, name='checkout'),
    path('pedidos/', views.pedido_lista_view, name='pedido_lista'),
    path('pedido/<int:pk>/', views.pedido_detalhe_view, name='pedido_detalhe'),
    path('pedido/<int:pk>/simular-pagamento/', views.pedido_simular_pagamento_view, name='pedido_simular_pagamento'),
    path('pedido/<int:pk>/avancar/', views.pedido_avancar_view, name='pedido_avancar'),
    # Usuario:
    path('perfil/', views.perfil_view, name='perfil'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    # path('cadastro/verificar/', views.verificar_cadastro_view, name='verificar_cadastro'),
    # path('cadastro/reenviar/', views.reenviar_codigo_view, name='reenviar_codigo'),
    path('login/', views.login_view, name='login'),
    path('login/verificar/', views.verificar_login_view, name='verificar_login'),
    path('login/reenviar/', views.reenviar_codigo_login_view, name='reenviar_codigo_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # endereço:
    path('endereco/novo/', views.endereco_adicionar, name='endereco_adicionar'),
    path('endereco/<int:pk>/editar/', views.endereco_editar, name='endereco_editar'),
    path('endereco/<int:pk>/remover/', views.endereco_remover, name='endereco_remover'),
    # Dashboard (staff)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/usuarios/', views.dashboard_usuarios_view, name='dashboard_usuarios'),
    path('dashboard/pedidos/', views.dashboard_pedidos_view, name='dashboard_pedidos'),
    path('produto/novo/', views.produto_criar, name='produto_criar'),
    path('produto/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('categoria/nova/', views.categoria_criar, name='categoria_criar'),
    path('categoria/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
] 