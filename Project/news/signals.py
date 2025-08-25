from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        subject = 'Добро пожаловать в NewsPortal!'
        message = render_to_string('emails/welcome.html', {
            'user': instance,
            'site_url': settings.SITE_URL
        })

        try:
            send_mail(
                subject=subject,
                message='',
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки приветственного письма: {e}")