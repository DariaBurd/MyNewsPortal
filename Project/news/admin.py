from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_type', 'author', 'created_at', 'rating')
    list_filter = ('post_type', 'categories', 'created_at')
    search_fields = ('title', 'text')

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(PostCategory)
admin.site.register(Comment)
