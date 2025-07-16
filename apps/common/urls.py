from django.urls import path
from .views import (
    StaticPageListView,
    StaticPageDetailView,
    regions_with_districts,
    app_settings
)

urlpatterns = [
    path('common/pages/', StaticPageListView.as_view(), name='static-pages-list'),
    path('common/pages/<slug:slug>/', StaticPageDetailView.as_view(), name='static-page-detail'),
    path('common/regions-with-districts/', regions_with_districts, name='regions-with-districts'),
    path('common/setting/', app_settings, name='app-settx   ings'),
]