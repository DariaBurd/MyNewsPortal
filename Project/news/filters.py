from django_filters import FilterSet, DateFilter, CharFilter
from .models import Post
from django import forms


class PostFilter(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    author__user__username = CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Автор',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    created_after = DateFilter(
        field_name='created_at',
        lookup_expr='gt',
        label='Позже указанной даты',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Post
        fields = []