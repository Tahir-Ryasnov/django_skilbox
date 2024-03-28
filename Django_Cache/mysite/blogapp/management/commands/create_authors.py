from django.core.management import BaseCommand

from blogapp.models import Author


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Create Authors')
        authors_name = [
            "Tahir",
            "Ksuwa",
        ]
        for i_name in authors_name:
            author, created = Author.objects.get_or_create(name=i_name)
            self.stdout.write(f'created author {i_name}')
        self.stdout.write(self.style.SUCCESS("Authors created"))
