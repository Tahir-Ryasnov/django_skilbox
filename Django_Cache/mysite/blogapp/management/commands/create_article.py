from typing import Sequence
from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Author, Category, Tag, Article


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Create article')

        author = Author.objects.get(name='Tahir')
        category = Category.objects.get(name="news")
        tags: Sequence[Tag] = Tag.objects.defer("id").all()
        article, created = Article.objects.get_or_create(
            title="Third article",
            content="there is no content here",
            author=author,
            category=category,
        )
        for tag in tags:
            article.tags.add(tag)
        self.stdout.write(f'Created article {article}')