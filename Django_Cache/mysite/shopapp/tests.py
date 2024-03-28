from random import choices
from string import ascii_letters

from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEquals(result, 5)


# class ProductCreateViewTestCase(TestCase):
#     def setUp(self) -> None:
#         self.product_name = "".join(choices(ascii_letters, k=10))
#         Product.objects.filter(name=self.product_name).delete()
#
#     def test_create_product(self):
#         response = self.client.post(
#             reverse("shopapp:product_create"),
#             {
#                 "name": self.product_name,
#                 "price": "1234.45",
#                 "description": "A good table",
#                 "discount": "10",
#             }
#         )
#         self.assertRedirects(response, reverse("shopapp:products_list"))
#         self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     cls.product = Product.objects.create(name="Best Product")

    # @classmethod
    # def tearDownClass(cls):
    #     cls.product.delete()

    def setUp(self) -> None:
        self.product = Product.objects.create(name="Best Product")

    def tearDown(self) -> None:
        self.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_contant(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


# class ProductListViewTestCase(TestCase):
#     fixtures = [
#         "products-fixture.json",
#     ]
#
#     def test_products(self):
#         response = self.client.get(reverse("shopapp:products_list"))
#         self.assertQuerysetEqual(
#             qs=Product.objects.filter(archived=False).all(),
#             values=(p.pk for p in response.context["products"]),
#             transform=lambda p: p.pk,
#         )
#         self.assertTemplateUsed(response, "shopapp/products_list.html")

class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="bob", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(
            username="test username", password="qwerty")
        permission_view_order = Permission.objects.get(
            codename="view_order",
        )

        cls.user.user_permissions.add(permission_view_order)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='test delivery address',
            promocode='test promocode',
            user_id=self.user.id,
        )

    def tearDown(self):
        self.order.delete()
        self.client.logout()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )
        # есть ли в теле ответа адрес заказа
        self.assertContains(response=response, text="test delivery address")
        # есть ли в теле ответа промокод
        self.assertContains(response=response, text="test promocode")
        # в контексте ответа тот же заказ, который был создан перед тестом
        self.assertContains(response, f"Order №{self.order.pk}")


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
        'users-fixture'
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"),)
        self.assertEqual(response.status_code, 200)

        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data["products"], expected_data)


class OrderExportViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        call_command('loaddata', 'users-fixture', verbosity=0)
        call_command('loaddata', 'products-fixture', verbosity=0)
        call_command('loaddata', 'orders-fixture', verbosity=0)
        cls.user = User.objects.create_user(
            username="test_1",
            password="test_1",
            is_staff='1',
            is_superuser='1'
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()

    def test_get_orders_view(self):
        response = self.client.get(reverse("shopapp:order-export"))
        # статус ответа 200
        self.assertEqual(response.status_code, 200)

        orders_data = response.json()
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "ID": order.pk,
                "delivery address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.id,
                "products id": str([product.pk for product in order.products.all()]),
            }
            for order in orders
        ]
        # в JSON - теле ответа ожидаемые значения
        self.assertEqual(orders_data["orders"], expected_data)
