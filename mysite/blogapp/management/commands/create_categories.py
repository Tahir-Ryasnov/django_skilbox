from django.core.management import BaseCommand

from blogapp.models import Category


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Create Categories')
        categories_names = [
            "sport",
            "trips",
            "food",
            "art",
            "news",
        ]
        for i_name in categories_names:
            category, created = Category.objects.get_or_create(name=i_name)
            self.stdout.write(f'created category {i_name}')
        self.stdout.write(self.style.SUCCESS("Categories created"))
