from errno import ENAMETOOLONG

from django.urls import path
from . import views
from .serializers import StaticPageListSerializer

urlpatterns = [
    path('regions-with-districts/', views.RegionsWithDistrictsListView.as_view(), name='regions-with-districts'),
    path(
        "pages/<slug:slug>/",
        views.StaticPageDetailView.as_view(),
        name="static-page-detail",
    ),
    path('pages/',views.StaticPageListView.as_view(),name='pages'),
    path("settings/", views.SettingDetailView.as_view(), name="settings"),
]
