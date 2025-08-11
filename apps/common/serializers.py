from rest_framework import serializers
from .models import Region, District, StaticPage, Setting


class DistrictSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

class RegionWithDistrictsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    districts = DistrictSerializer(many=True, read_only=True)

class StaticPageListSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True)
    title = serializers.CharField(read_only=True)

class SettingSerializer(serializers.Serializer):
    phone = serializers.CharField(read_only=True)
    support_email = serializers.EmailField(read_only=True)
    working_hours = serializers.CharField(read_only=True)
    maintenance_mode = serializers.BooleanField(read_only=True)
