from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Create products')
        products_names = [
            "BIG",
            "MIIDLE",
            "LITTLE",
        ]
        for i_name in products_names:
            product, created = Product.objects.get_or_create(name='good')
            self.stdout.write(f'created product {i_name}')
        self.stdout.write(self.style.SUCCESS("Products created"))
