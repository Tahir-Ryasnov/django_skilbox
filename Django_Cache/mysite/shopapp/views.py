"""
В этом модуле лежат различные наборы представлений для интернет-магазина.

views по товарам, заказам и т.д.
"""
import logging
from csv import DictWriter
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse, Http404,
)
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)

from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import ProductForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer
from .common import save_scv_products

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

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print("hello products list")
        return super().list(*args, **kwargs)

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

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content_Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response


    @action(
        detail=False,
        methods=["post", ],
        parser_classes=[MultiPartParser, ]
    )
    def upload_csv(self, request: Request):
        products = save_scv_products(
            file=request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["delivery_address", "products"]
    filterset_fields = ["delivery_address", "promocode", "created_at", "user", "products",]
    ordering_fields = ["delivery_address", "user", "products"]


# @method_decorator(cache_page(60 * 2))
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
        print("shop index context:", context)
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
        cache_key = "product_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
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
        # elem = products_data[0]
        # name = elem["name"]
        # print("name: ", name)
        cache.set(cache_key, products_data, 60 * 5)
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


class UserOrdersDataExportView(View):

    def get(self, request, **kwargs) -> JsonResponse:
        try:
            self.owner = User.objects.filter(pk=self.kwargs['pk'])[0]
        except IndexError:
            raise Http404
        cache_key = "product_data_export"
        products_data = cache.get(cache_key)
        orders = Order.objects.filter(user=self.owner).order_by("pk").all()
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
        cache.set(cache_key, products_data, 60 * 5)
        return JsonResponse({"orders": orders_data})


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes in the products presented"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Product.objects
            .filter(archived=False, )
            .order_by("-created_at")[:5]
        )

    def item_title(selfself, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]

    def item_link(self, item: Product):
        return reverse("shopapp:products_list", kwargs={"pk": item.pk})


class UserOrdersListView(ListView):
    template_name = "shopapp/user_orders_list.html"
    model = Order
    context_object_name = 'user_orders'


    def get_queryset(self):
        self.owner = self.kwargs["pk"]
        queryset = Order.objects.filter(user=self.owner).all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['owner'] = User.objects.filter(pk=self.owner)[0]
            return context
        except IndexError:
            raise Http404
