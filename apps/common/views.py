from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Region, District, StaticPage, Setting
from .serializers import RegionSerializer, DistrictSerializer, StaticPageSerializer, SettingSerializer


class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.AllowAny]


class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        region_id = self.request.query_params.get('region_id')
        if region_id:
            return District.objects.filter(region_id=region_id)
        return District.objects.all()


class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.filter(is_active=True)
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
def app_settings(request):
    settings = Setting.get_settings()
    serializer = SettingSerializer(settings)
    return Response(serializer.data)

