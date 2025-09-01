from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post
from .filters import PostFilter
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from .models import Post, Author
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from .models import Author


@login_required
def become_author(request):
    authors_group, created = Group.objects.get_or_create(name='authors')
    request.user.groups.add(authors_group)

    if not hasattr(request.user, 'author'):
        Author.objects.create(user=request.user)

    return redirect('profile')

class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    queryset = Post.objects.filter(post_type='NW')
    paginate_by = 10


class NewsDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    queryset = Post.objects.filter(post_type='NW')  # Добавляем фильтрацию только новостей


class ArticleList(ListView):
    model = Post
    template_name = 'news/article_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    queryset = Post.objects.filter(post_type='AR')


class ArticleDetail(DetailView):
    model = Post
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
    queryset = Post.objects.filter(post_type='AR')  # Добавляем фильтрацию только статей


def news_search(request):
    posts = Post.objects.filter(post_type='NW').order_by('-created_at')
    post_filter = PostFilter(request.GET, queryset=posts)
    paginator = Paginator(post_filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_search.html', {
        'filter': post_filter,
        'page_obj': page_obj
    })


class NewsCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    template_name = 'news/news_create.html'
    fields = ['title', 'text', 'categories']
    success_message = "Новость успешно создана!"

    def form_valid(self, form):
        form.instance.post_type = 'NW'
        form.instance.author = Author.objects.get(user=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.object.pk})


class NewsUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    template_name = 'news/news_edit.html'
    fields = ['title', 'text', 'categories']
    success_message = "Новость успешно обновлена!"

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')


class NewsDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')


class ArticleCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    template_name = 'news/article_create.html'
    fields = ['title', 'text', 'categories']
    success_message = "Статья успешно создана!"

    def form_valid(self, form):
        form.instance.post_type = 'AR'  # Устанавливаем тип "Статья"
        form.instance.author = Author.objects.get(user=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.object.pk})


class ArticleUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    template_name = 'news/article_edit.html'
    fields = ['title', 'text', 'categories']
    success_message = "Статья успешно обновлена!"

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')


class ArticleDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('article_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')


@login_required
def toggle_subscription(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    subscription, created = Subscription.objects.get_or_create(
        user=user,
        category=category
    )

    if not created:
        subscription.delete()
        is_subscribed = False
    else:
        is_subscribed = True

    return JsonResponse({
        'is_subscribed': is_subscribed,
        'subscribers_count': category.subscribers.count()
    })


def send_welcome_email(user):
    subject = 'Добро пожаловать в NewsPortal!'
    message = render_to_string('emails/welcome.html', {
        'user': user,
        'site_url': settings.SITE_URL
    })

    send_mail(
        subject=subject,
        message='Hello! Welcome to our News Portal!',
        html_message=message,
        from_email=zayka-energy@yandex.ru,
        recipient_list=[user.email],
        fail_silently=False,
    )

