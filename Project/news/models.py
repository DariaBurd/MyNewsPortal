from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
#from .tasks import send_new_post_notification


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = self.post_set.aggregate(pr=Sum('rating'))['pr'] or 0
        comments_rating = self.user.comment_set.aggregate(cr=Sum('rating'))['cr'] or 0
        posts_comments_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Sum('rating'))['pcr'] or 0

        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, through='Subscription', related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'category']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} - {self.category.name}'


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    text = models.TextField()
    excerpt = models.TextField(blank=True, verbose_name='Краткое содержание для рассылки')
    rating = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

    def send_new_post_notifications(self):
        for category in self.categories.all():
            subscribers = category.subscribers.all()

            for user in subscribers:
                if user.email:
                    subject = f'Новая статья в категории "{category.name}"'
                    message = render_to_string('emails/new_post.html', {
                        'user': user,
                        'post': self,
                        'category': category,
                        'site_url': settings.SITE_URL
                    })

                    try:
                        send_mail(
                            subject=subject,
                            message='',
                            html_message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Ошибка отправки email: {e}")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.excerpt and self.text:
            self.excerpt = self.text[:150] + '...' if len(self.text) > 150 else self.text

        super().save(*args, **kwargs)

        if is_new and self.is_published:
            send_new_post_notification.delay(self.id)


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Категория поста'
        verbose_name_plural = 'Категории постов'

    def __str__(self):
        return f'{self.post.title} - {self.category.name}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'Комментарий от {self.user.username} к {self.post.title}'