from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post
from .filters import PostFilter

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