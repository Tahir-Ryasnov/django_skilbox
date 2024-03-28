from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.utils.translation import gettext_lazy as _, ngettext

from .forms import ProfileForm
from .models import Profile


class HelloView(View):
    welcome_message = _("welcome hello world!")
    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class UsersListView(ListView):
    template_name = 'myauth/users-list.html'
    context_object_name = 'users'
    queryset = User.objects.all()
    users = User.objects.all()


class UserAboutMelView(UpdateView):
    template_name = 'myauth/user_detail_form.html'
    model = Profile
    context_object_name = 'profile'
    fields = "avatar",

    def get_success_url(self):
        return reverse(
            'myauth:user_details',
            kwargs={'pk': self.object.pk},
        )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class UserUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        else:
            object_pk = self.get_object().pk
            user_pk = self.request.user.pk
            if object_pk == user_pk:
                return True

    model = Profile
    fields = "avatar", "bio"

    def get_success_url(self):
        return reverse(
            'myauth:user_details',
            kwargs={'pk': self.object.pk},
        )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:users")

    def form_valid(self, form):
        response = super().form_valid(form)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        Profile.objects.create(user=user, id=user.pk)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')
        return render(request, 'myauth/login.html')
    username = request.POST['username']
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html",
                  {"error": "Invalid login authentication"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse('myauth:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return redirect('myauth:login')
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth:view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
