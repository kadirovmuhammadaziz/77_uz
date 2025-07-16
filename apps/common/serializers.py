from rest_framework import serializers
from .models import  StaticPage,Region,District,Setting

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id','name','guid']


class RegionWithDistrictsSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True,read_only=True)

    class Meta:
        model = Region
        fields =  [ 'id','name','districts','guid']


class StaticPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['slug','title']
    

class StaticPageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['slug','title','content','created_at', 'updated_at']


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model =Setting
        fields = ['phone','support_email','working_hours','app_version',"maintenance_mode"]

