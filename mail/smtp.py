from django.core.mail import EmailMultiAlternatives
from threading import Thread
from django.core import signing
from django.conf import settings
from utils.shortcuts import build_url


def SendRestoreMail(user):
    sign_pk = signing.dumps(user.pk, compress=True)
    url = build_url('accounts:set_new_password', signed_pk=sign_pk)
    url = 'http://{host}{url}'.format(host=settings.ALLOWED_HOSTS[0], url=url)

    subject, from_email = f'Восстановление пароля на {settings.ALLOWED_HOSTS[0]}', settings.EMAIL_HOST_USER
    text_content = f'Вы сделали запрос на восстановленин пароля. \n' \
                   f'Для восстановления пароля перейдите по ссылке: {url}\n' \
                    'Ссылка действительна 15 минут.' \
                   f'Если запрос делали не вы, можете проигнорировать это пиьсмо.'
    html_content = text_content.replace('\n', '<br>')
    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    t = Thread(target=send, args=[msg])
    t.setDaemon(True)
    t.start()


def send(msg):
    msg.send(fail_silently=False)