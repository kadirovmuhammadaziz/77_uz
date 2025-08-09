from rest_framework import generics
from django.db.models import Prefetch
from .models import Region, District, StaticPage, Setting
from .serializers import (
    RegionWithDistrictsSerializer,
    DistrictSerializer,
    StaticPageSerializer,
    StaticPageListSerializer,
    SettingSerializer,
)
from .utils.custom_response_decorator import custom_response


@custom_response
class RegionsWithDistrictsListView(generics.ListAPIView):
    serializer_class = RegionWithDistrictsSerializer

    def get_queryset(self):
        return Region.objects.prefetch_related(
            Prefetch('districts', queryset=District.objects.all())
        ).all()


@custom_response
class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.filter(is_active=True)
    serializer_class = StaticPageSerializer
    lookup_field = "slug"


@custom_response
class StaticPageListView(generics.ListAPIView):
    serializer_class = StaticPageListSerializer

    def get_queryset(self):
        return StaticPage.objects.filter(is_active=True).order_by('id')


@custom_response
class SettingDetailView(generics.RetrieveAPIView):
    serializer_class = SettingSerializer

    def get_object(self):
        return Setting.get_settings()
