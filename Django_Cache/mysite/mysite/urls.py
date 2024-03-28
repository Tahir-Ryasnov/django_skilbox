from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .sitemaps import sitemaps

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path('admin/', admin.site.urls),
    path('shop/', include('shopapp.urls')),
    path('req/', include('requestdataapp.urls')),
    path('accounts/', include("myauth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="dedoc"),
    path("api/", include("myapiapp.urls")),
]

urlpatterns += i18n_patterns(
    path('shop/', include('shopapp.urls')),
    path('req/', include('requestdataapp.urls')),
    path('accounts/', include("myauth.urls")),
    path("blogapp/", include("blogapp.urls")),
    path("blog/", include("blogapp_new.urls")),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap"
    )
)

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
