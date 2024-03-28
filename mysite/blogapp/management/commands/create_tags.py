from django.core.management import BaseCommand

from blogapp.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Create Tags')
        tags_names = [
            "ihavenoideatag",
            "some tag",
            "love",
        ]
        for i_name in tags_names:
            tag, created = Tag.objects.get_or_create(name=i_name)
            self.stdout.write(f'created tag {i_name}')
        self.stdout.write(self.style.SUCCESS("Tags created"))
