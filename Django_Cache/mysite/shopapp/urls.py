from django.urls import path, include
from rest_framework import routers

from shopapp.views import (
    ShopIndexView,
    GroupsListView,
    ProductDetailView,
    ProductListView,
    OrdersListView,
    OrderDetailView,
    OrderUpdateView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderCreateView,
    OrderDeleteView,
    ProductsDataExportView,
    OrderDataExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed,
)

routers = routers.DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

app_name = 'shopapp'

urlpatterns = [
    # path('', cache_page(60 * 3)(ShopIndexView.as_view()), name='index'),
    path('', ShopIndexView.as_view(), name='index'),
    path("api/", include(routers.urls)),
    path('groups/', GroupsListView.as_view(), name='groups_list'),
    path('products/', ProductListView.as_view(), name='products_list'),
    path("products/latest/feed", LatestProductsFeed(), name="products-feed"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>', ProductDetailView.as_view(), name='product_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='product_delete'),
    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path("orders/export/", OrderDataExportView.as_view(), name="order-export"),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order_details'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
]
