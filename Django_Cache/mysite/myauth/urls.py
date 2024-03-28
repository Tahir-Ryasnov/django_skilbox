from django.urls import path
from django.contrib.auth.views import LoginView

from myauth.views import (
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    logout_view,
    MyLogoutView,
    UserUpdateView,
    RegisterView,
    FooBarView,
    UsersListView,
    UserAboutMelView,
    HelloView,
)
from shopapp.views import UserOrdersListView, UserOrdersDataExportView


app_name = 'myauth'

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<int:pk>/about-me", UserAboutMelView.as_view(), name="user_details"),
    path("users/<int:pk>/update", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/orders/", UserOrdersListView.as_view(), name="user_orders_list"),
    path("users/<int:pk>/orders/export/", UserOrdersDataExportView.as_view(), name="user_orders_export"),
    path('login/',
         LoginView.as_view(
             template_name='myauth/login.html',
             redirect_authenticated_user=True,
         ),
         name="login"),
    path("logout/", logout_view, name="logout"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),
    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]
