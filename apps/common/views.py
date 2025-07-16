from collections import defaultdict

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import StaticPage, Region, Setting
from .serializers import (
    StaticPageListSerializer,
    StaticPageDetailSerializer,
    RegionWithDistrictsSerializer,
    SettingSerializer
)


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param ='limit '
    max_page_size = 100

    def get_paginated_response(self):
        return Response({
            'count':self.page.paginator.count,
            'next':self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class StaticPageListView(generics.ListAPIView):
    queryset = StaticPage.objects.all().order_by('-created_at')
    serializer_class = StaticPageListSerializer
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        return StaticPage.objects.all().order_by('-created_at')


class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageDetailSerializer
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        try:
            return StaticPage.objects.get(slug=slug)
        except StaticPage.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="Statik sahifa topilmadi")


@api_view(['GET'])
def regions_with_districts(request):
    try:
        limit = request.GET.get('limit',10)
        offset = request.GET.get('offset',0)

        try:
            limit = int(limit)
            offset = int(offset)
        except ValueError:
            limit = 10
            offset = 0


        regions = Region.objects.prefetch_related('districts').all()[offset:offset + limit]
        serializer = RegionWithDistrictsSerializer(regions,many=True)


        return Response(serializer.data,status=status.HTTP_220_Ok)

    except Exception as a:
        return Response(
            {"error": "Ma'lumotlarni olishda xatolik yuz berdi"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def app_settings(request):
    try:
        settings,created = Setting.objects.get_or_create(
            defaults={
                'phone': '+998770367366',
                'support_email': 'support@77.uz',
                'working_hours': 'Dushanba-Yakshanba 9:00-21:00',
                'app_version': '1.2.3',
                'maintenance_mode': False
            }
        )

        serializer = SettingSerializer(settings)
        return Response(serializer.data,status=status.HTTP_220_Ok)

    except Exception as e:
        return  Response(
            {"error":"Sozlamalarni olishdda xatolik yuz berdi"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



