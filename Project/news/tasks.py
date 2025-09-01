from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Post, Category, Subscription
from datetime import datetime, timedelta
from django.utils import timezone


@shared_task
def send_new_post_notification(post_id):
    try:
        post = Post.objects.get(id=post_id)

        for category in post.categories.all():
            subscribers = category.subscribers.all()

            for user in subscribers:
                if user.email:
                    subject = f'Новая статья в категории "{category.name}"'
                    message = render_to_string('emails/new_post.html', {
                        'user': user,
                        'post': post,
                        'category': category,
                        'site_url': settings.SITE_URL
                    })

                    send_mail(
                        subject=subject,
                        message='',
                        html_message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )

    except Post.DoesNotExist:
        print(f"Post with id {post_id} does not exist")


@shared_task
def send_weekly_digest():
    """Еженедельная рассылка новых статей"""
    week_ago = timezone.now() - timedelta(days=7)

    for category in Category.objects.all():
        new_posts = Post.objects.filter(
            categories=category,
            created_at__gte=week_ago,
            is_published=True
        )

        if new_posts.exists():
            subscribers = category.subscribers.all()

            for user in subscribers:
                if user.email:
                    subject = f'Еженедельный дайджест: {category.name}'
                    message = render_to_string('emails/weekly_digest.html', {
                        'user': user,
                        'category': category,
                        'posts': new_posts,
                        'site_url': settings.SITE_URL,
                        'week_start': week_ago
                    })

                    send_mail(
                        subject=subject,
                        message='',
                        html_message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )