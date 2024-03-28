"""
В этом модуле лежат различные наборы представлений для интернет-магазина.

views по товарам, заказам и т.д.
"""
import logging
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.utils.translation import gettext_lazy as _, ngettext
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

import datetime


log = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.
    Полный CRUD для сущностей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        "name",
        "description",
    ]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "description",
        "price",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["delivery_address", "products"]
    filterset_fields = ["delivery_address", "promocode", "created_at", "user", "products",]
    ordering_fields = ["delivery_address", "user", "products"]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('BIG', 1000),
            ('MIDDLE', 500),
            ('LITTLE', 100),
        ]

        context = {
            'current_time': datetime.datetime.now(),
            'products': products,
            "items": 2,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop_index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest):
        context = {
            'form': GroupForm,
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups_list.html',  context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductListView(ListView):
    template_name = 'shopapp/products_list.html'
    # model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)

    # Если наследуется от TemplateView
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['products'] = Product.objects.all()
    #     return context


class ProductDetailView(DetailView):
    template_name = 'shopapp/product-details.html'
    queryset = Product.objects.prefetch_related("images")
    context_object_name = 'product'


class ProductCreateView(PermissionRequiredMixin, CreateView):
    # def test_func(self):
    #     # return self.request.user.groups.filter(name="secret-group").exists()
    #     return self.request.user.is_superuser

    permission_required = "shopapp.add_product"
    model = Product
    fields = 'name', 'price', 'description', 'discount', "preview"
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            object_pk = self.get_object().created_by.pk
            user_pk = self.request.user.pk
            if self.request.user.has_perm("shopapp.change_product") and object_pk == user_pk:
                return True
    model = Product
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/order_list.html"
    context_object_name = 'orders'
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    template_name = 'shopapp/order_detail.html'
    model = Order
    context_object_name = 'order'


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'user', 'delivery_address', 'promocode', 'products'
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk},
        )


class OrderCreateView(CreateView):
    model = Order
    fields = 'user', 'delivery_address', 'promocode', 'products'
    success_url = reverse_lazy('shopapp:orders_list')


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name: ", name)
        return JsonResponse({"products": products_data})


class OrderDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "ID": order.pk,
                "delivery address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.id,
                "products id": str([product.pk for product in order.products.all()]),
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})
