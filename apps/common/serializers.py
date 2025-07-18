from rest_framework import serializers
from .models import Region, District, StaticPage, Setting


class RegionSerializer(serializers.ModelSerializer):
    districts_count = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'guid', 'name', 'districts_count', 'created_time']

    def get_districts_count(self, obj):
        return obj.districts.count()


class DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = District
        fields = ['id', 'guid', 'name', 'region', 'region_name', 'created_time']


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['id', 'guid', 'slug', 'title', 'content', 'meta_description', 'is_active']


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            'phone', 'support_email', 'working_hours', 'app_name',
            'app_logo', 'privacy_policy_url', 'terms_of_service_url',
            'facebook_url', 'instagram_url', 'telegram_url',
            'delivery_fee', 'free_delivery_minimum', 'maintenance_mode'
        ]