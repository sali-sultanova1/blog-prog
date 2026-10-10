import django_filters
from .models import Article

class ArticleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="categories__slug")
    tag = django_filters.CharFilter(field_name="tags__slug")
    author = django_filters.NumberFilter(field_name="author_id")
    status = django_filters.ChoiceFilter(choices=Article.Status.choices)

    class Meta:
        model = Article
        fields = ["category", "tag", "author", "status"]