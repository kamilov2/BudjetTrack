from django.conf import settings
from django.urls import include, re_path, path
from django.contrib import admin
from django.views.static import serve
from django.conf.urls.static import static
import debug_toolbar
from main.urls import urlpatterns as main_urls
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from silk import views

schema_view = get_schema_view(
    openapi.Info(
        title="Budjet Track",
        default_version='v1',
        description="Budjet Track API",
        terms_of_service="https://t.me/kamilov_jasur",
        contact=openapi.Contact(email="jasurkamilov@gmail.com"),
        license=openapi.License(name="№125868"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(main_urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("silk/", include("silk.urls", namespace="silk")),
]
urlpatterns += [
    path('', RedirectView.as_view(url='api/register', permanent=True)),
]
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
