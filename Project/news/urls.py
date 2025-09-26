from django.urls import path
from .views import (
    NewsList, NewsDetail, NewsCreate, NewsUpdate, NewsDelete,
    ArticleList, ArticleDetail, ArticleCreate, ArticleUpdate, ArticleDelete, become_author
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PostViewSet, CategoryViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'api/posts', PostViewSet, basename='post')
router.register(r'api/categories', CategoryViewSet, basename='category')
router.register(r'api/comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Новости
    path('', NewsList.as_view(), name='news_list'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),

    # Статьи
    path('articles/', ArticleList.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetail.as_view(), name='article_detail'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
    path('become-author/', become_author, name='become_author'),

    path('', include(router.urls)),
    path('api/news/', PostViewSet.as_view({'get': 'news'}), name='api-news'),
    path('api/articles/', PostViewSet.as_view({'get': 'articles'}), name='api-articles'),
]