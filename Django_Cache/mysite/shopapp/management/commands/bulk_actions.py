from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Start demo bulk actions')

        result = Product.objects.filter(
            name__contains="product",
        ).update(discount=10)

        print(result)

        # info = [
        #     ("product 1", 100),
        #     ("product 2", 200),
        #     ("product 3", 300),
        # ]
        # products = [
        #     Product(name=name, price=price)
        #     for name, price in info
        # ]
        #
        # result = Product.objects.bulk_create(products)
        #
        # for obj in result:
        #     print(obj)

        self.stdout.write(f'Done')
