from rest_framework import serializers
from .models import Region, District, StaticPage, Setting


class RegionSerializer(serializers.ModelSerializer):
    district_count = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ["id", "guid", "name", "districts_count", "created_time"]

        def get_district_count(self, obj):
            return obj.district.count()


class DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = District
        fields = ["id", "guid", "name", "region", "region_name", "created_time"]


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = [
            "id",
            "guid",
            "slug",
            "title",
            "content",
            "meta_description",
            "is_active",
        ]


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ["phone", "support_email", "working_hours", "maintenance_mode"]
