# accounts/utils.py
from django.conf import settings
import secrets
from datetime import timedelta
from django.utils import timezone
from .models import DispositivoConfiavel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


def enviar_codigo_email(usuario, codigo, tipo):
    if tipo == 'cadastro':
        assunto = "ManiaGeek — Confirme seu cadastro"
        corpo_texto = (
            f"Olá, {usuario.display_name or usuario.username}!\n\n"
            f"Seu código de verificação é: {codigo}\n\n"
            f"Ele expira em 10 minutos."
        )
        corpo_html = f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
          <h2 style="color: #45277e;">ManiaGeek</h2>
          <p>Olá, <strong>{usuario.display_name or usuario.username}</strong>!</p>
          <p>Seu código de verificação é:</p>
          <p style="font-size: 32px; font-weight: bold; letter-spacing: 8px;
                    color: #221343; background: #f5f5f5; padding: 16px;
                    text-align: center; border-radius: 8px;">{codigo}</p>
          <p style="color: #888; font-size: 12px;">Ele expira em 10 minutos.</p>
        </div>
        """
    else:  # login
        assunto = "ManiaGeek — Código de acesso"
        corpo_texto = (
            f"Olá, {usuario.display_name or usuario.username}!\n\n"
            f"Seu código de acesso é: {codigo}\n\n"
            f"Se não foi você, troque sua senha."
        )
        corpo_html = f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
          <h2 style="color: #45277e;">ManiaGeek</h2>
          <p>Olá, <strong>{usuario.display_name or usuario.username}</strong>!</p>
          <p>Alguém está tentando entrar na sua conta. Seu código é:</p>
          <p style="font-size: 32px; font-weight: bold; letter-spacing: 8px;
                    color: #221343; background: #f5f5f5; padding: 16px;
                    text-align: center; border-radius: 8px;">{codigo}</p>
          <p style="color: #888; font-size: 12px;">
            Se não foi você, troque sua senha imediatamente.
          </p>
        </div>
        """
    message = Mail(
        from_email=Email(settings.SENDGRID_FROM_EMAIL, "ManiaGeek"),
        to_emails=To(usuario.email),
        subject=assunto,
    )
    message.content = [
        Content("text/plain", corpo_texto),
        Content("text/html", corpo_html),
    ]
    sg = SendGridAPIClient(settings.SENDGRID_KEY)
    response = sg.send(message)
    if response.status_code not in (200, 201, 202):
        raise RuntimeError(
            f"SendGrid retornou {response.status_code}: {response.body}"
        )

def gerar_token_dispositivo(usuario):
    DispositivoConfiavel.objects.filter(usuario=usuario).delete()
    token = secrets.token_urlsafe(48)
    return DispositivoConfiavel.objects.create(
        usuario=usuario,
        token=token,
        expira_em=timezone.now() + timedelta(days=30),
    )
def token_dispositivo_valido(token):
    if not token:
        return None
    try:
        disp = DispositivoConfiavel.objects.get(token=token)
    except DispositivoConfiavel.DoesNotExist:
        return None
    if not disp.valido():
        disp.delete()
        return None
    return disp
def ultimo_codigo_recente(usuario, tipo, segundos=60):
    ultimo = usuario.codigos_verificacao.filter(tipo=tipo).first()
    if not ultimo:
        return False
    delta = timezone.now() - ultimo.criado_em
    return delta.total_seconds() < segundos