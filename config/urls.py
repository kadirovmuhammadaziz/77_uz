from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Django setting modulini aniqlash (dev/prod)
DJANGO_SETTINGS_MODULE = getattr(settings, "DJANGO_SETTINGS_MODULE", "development")


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = (
            ["http"] if DJANGO_SETTINGS_MODULE == "development" else ["https"]
        )
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="Sizning loyihangiz API",
        default_version="v1",
        description="API documentation for your project",
        terms_of_service="https://your.domain/terms/",
        contact=openapi.Contact(email="support@your.domain"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=BothHttpAndHttpsSchemaGenerator,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.urls"), name="accounts"),
    path("api/v1/common/", include("common.urls"), name="common"),
    path("api/v1/store/", include("store.urls"), name="store"),
]

if DJANGO_SETTINGS_MODULE == "development":
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
