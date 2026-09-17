from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView

urlpatterns = [
    path('', views.home_view, name='home'),
    path('produto/', views.produtos_view, name='produtos'),
    path('produto/<int:id>/', views.detalhe_produto, name='detalhe_produto'),
    # Administrador (temporario)
    path('produto/novo/', views.produto_criar, name='produto_criar'),
    path('produto/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('categoria/nova/', views.categoria_criar, name='categoria_criar'),
    path('categoria/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    # Usuario:
    path('perfil/', views.perfil_view, name='perfil'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
] 