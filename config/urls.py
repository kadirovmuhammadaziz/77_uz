from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("default-admin-panel/", admin.site.urls),
]

urlpatterns += [
    path("api/v1/common/", include("common.urls"), name="common"),
    path("api/v1/accounts/", include("accounts.urls"), name="accounts"),
    path("api/v1/store/", include("store.urls"), name="store"),
]

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
