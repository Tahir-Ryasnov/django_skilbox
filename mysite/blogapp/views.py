from django.shortcuts import render
from django.views.generic import ListView

from .models import Article


class ArticleListView(ListView):
    """Class Based View для отображения списка статей"""

    template_name = "blogapp/articles_list.html"
    context_object_name = "articles"
    queryset = (
        Article.objects.select_related("author", "category").prefetch_related("tags").defer("content")
    )
