from rest_framework import generics
from .models import Region, District, StaticPage, Setting
from .serializers import (
    RegionSerializer,
    DistrictSerializer,
    StaticPageSerializer,
    SettingSerializer,
)
from .utils.custom_response_decorator import custom_response


@custom_response
class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


@custom_response
class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        region_id = self.request.query_params.get("region_id")
        if region_id:
            return District.objects.filter(region_id=region_id)
        return District.objects.all()


@custom_response
class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.filter(is_active=True)
    serializer_class = StaticPageSerializer
    lookup_field = "slug"


@custom_response
class SettingDetailView(generics.RetrieveAPIView):
    serializer_class = SettingSerializer

    def get_object(self):
        return Setting.get_settings()
