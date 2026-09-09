from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('produto/', views.produtos_view, name='produtos'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
]