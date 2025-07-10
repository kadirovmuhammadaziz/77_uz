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

    def get_paginated_response(sel):