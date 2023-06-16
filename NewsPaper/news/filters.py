from django_filters import FilterSet, DateFilter, CharFilter
from .models import Post


class NewsFilter(FilterSet):
    creation_time_newer = DateFilter(field_name='creation_time', label='новее чем:', lookup_expr='gt')
    creation_time_older = DateFilter(field_name='creation_time', label='старше чем:', lookup_expr='lt')
    author_name = CharFilter(field_name='author__user__username', label='имя автора:', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = []
