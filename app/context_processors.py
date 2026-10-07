def carrinho_contexto(request):
    try:
        from .models import Carrinho
        if not request.user.is_authenticated and not request.session.session_key:
            return {'carrinho_navbar': None}
        carrinho = Carrinho.obter_para_request(request)
        return {'carrinho_navbar': carrinho}
    except Exception:
        return {'carrinho_navbar': None}