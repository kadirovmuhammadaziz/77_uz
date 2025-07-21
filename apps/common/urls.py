from django.urls import path
from . import views

urlpatterns = [
    path('regions/', views.RegionListView.as_view(), name='region-list'),
    path('districts/', views.DistrictListView.as_view(), name='district-list'),
    path('pages/<slug:slug>/', views.StaticPageDetailView.as_view(), name='static-page-detail'),
    path('settings/', views.app_settings, name='app-settings'),
]
