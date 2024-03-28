from django.db import models


class Author(models.Model):
    """Модель Author представляет автора статьи"""

    name = models.CharField(max_length=100)
    bio = models.TextField(null=False, blank=True)

    def __str__(self) -> str:
        return str(self.name)


class Category(models.Model):
    """Модель Category представляет категорию статьи"""

    name = models.CharField(max_length=40)


class Tag(models.Model):
    """Модель Tag представляет тэг, который можно назначить статье"""

    name = models.CharField(max_length=20)


class Article(models.Model):
    """Модель Article представляет статью"""

    title = models.CharField(max_length=200)
    content = models.TextField(null=False, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    def __str__(self) -> str:
        return f'{self.title!r}'
