from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import (
    Category,
    Ad,
    AdPhoto,
    FavoriteProduct,
    SavedSearch,
    SearchCount,
    PopularSearch,
)
from .serializers import (
    CategorySerializer,
    CategoryWithChildrenSerializer,
    AdListSerializer,
    AdDetailSerializer,
    AdCreateUpdateSerializer,
    AdPhotoCreateSerializer,
    FavoriteProductSerializer,
    SavedSearchSerializer,
    SearchCountSerializer,
    PopularSearchSerializer,
    SearchResultSerializer,
    AutoCompleteSerializer,
)
from .filters import AdFilter
from .permissions import IsOwnerOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# Category Views
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination


class CategoryWithChildrenView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategoryWithChildrenSerializer
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent__isnull=True).order_by(
            "order", "name"
        )


class SubCategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent__id"]

    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent__isnull=False).order_by(
            "order", "name"
        )


# Ad Views
class AdListView(generics.ListAPIView):
    queryset = Ad.objects.filter(status="active")
    serializer_class = AdListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = AdFilter
    search_fields = ["name", "description"]
    ordering_fields = ["published_at", "price", "view_count"]
    ordering = ["-is_top", "-published_at"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = (
            Ad.objects.filter(status="active")
            .select_related("seller", "category", "region", "district")
            .prefetch_related("photos")
        )

        category_ids = self.request.query_params.get("category_ids")
        if category_ids:
            try:
                category_list = [int(x.strip()) for x in category_ids.split(",")]
                queryset = queryset.filter(category_id__in=category_list)
            except (ValueError, TypeError):
                pass

        return queryset


class AdDetailView(generics.RetrieveAPIView):
    queryset = Ad.objects.filter(status="active")
    serializer_class = AdDetailSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AdCreateView(generics.CreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class MyAdListView(generics.ListAPIView):
    serializer_class = AdListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return (
            Ad.objects.filter(seller=self.request.user)
            .select_related("category", "region", "district")
            .prefetch_related("photos")
        )


class MyAdDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdDetailSerializer
        return AdCreateUpdateSerializer


class ProductDownloadView(generics.RetrieveAPIView):
    queryset = Ad.objects.filter(status="active")
    serializer_class = AdDetailSerializer
    lookup_field = "slug"


class AdPhotoCreateView(generics.CreateAPIView):
    queryset = AdPhoto.objects.all()
    serializer_class = AdPhotoCreateSerializer
    permission_classes = [IsAuthenticated]


class FavoriteProductListView(generics.ListAPIView):
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["ad__category"]

    def get_queryset(self):
        return FavoriteProduct.objects.filter(user=self.request.user).select_related(
            "ad__seller", "ad__category", "ad__region", "ad__district"
        )


class FavoriteProductByIdListView(generics.ListAPIView):
    serializer_class = FavoriteProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["device_id"]

    def get_queryset(self):
        device_id = self.request.query_params.get("device_id")
        if device_id:
            return FavoriteProduct.objects.filter(device_id=device_id).select_related(
                "ad__seller", "ad__category", "ad__region", "ad__district"
            )
        return FavoriteProduct.objects.none()


class FavoriteProductCreateView(generics.CreateAPIView):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        ad_id = request.data.get("product")
        if not ad_id:
            return Response(
                {"error": "Product ID talab qilinadi"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if FavoriteProduct.objects.filter(user=request.user, ad_id=ad_id).exists():
            return Response(
                {"error": "Mahsulot allaqachon sevimlilarga qo'shilgan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class FavoriteProductCreateByIdView(generics.CreateAPIView):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer

    def create(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        product_id = request.data.get("product")

        if not device_id or not product_id:
            return Response(
                {"error": "Device ID va Product ID talab qilinadi"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if FavoriteProduct.objects.filter(
            device_id=device_id, ad_id=product_id
        ).exists():
            return Response(
                {"error": "Mahsulot allaqachon sevimlilarga qo'shilgan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class FavoriteProductDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteProduct.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteProductDeleteByIdView(APIView):

    def delete(self, request, id):
        try:
            if request.user.is_authenticated:
                favorite = FavoriteProduct.objects.get(user=request.user, id=id)
            else:
                device_id = request.data.get("device_id")
                if not device_id:
                    return Response(
                        {"error": "Device ID talab qilinadi"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                favorite = FavoriteProduct.objects.get(device_id=device_id, id=id)

            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteProduct.DoesNotExist:
            return Response(
                {"error": "Sevimli mahsulot topilmadi"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SavedSearchCreateView(generics.CreateAPIView):
    queryset = SavedSearch.objects.all()
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]


class SavedSearchListView(generics.ListAPIView):
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user).select_related(
            "category"
        )


class SavedSearchDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)


class CategoryProductSearchView(generics.ListAPIView):
    serializer_class = SearchResultSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()
        if not query:
            return []

        results = []

        categories = Category.objects.filter(
            Q(name__icontains=query) & Q(is_active=True)
        )[:5]

        for category in categories:
            results.append(
                {
                    "id": category.id,
                    "name": category.name,
                    "type": "category",
                    "icon": category.icon.url if category.icon else None,
                }
            )

        ads = Ad.objects.filter(
            Q(name__icontains=query) & Q(status="active")
        ).select_related("category")[:5]

        for ad in ads:
            results.append(
                {
                    "id": ad.id,
                    "name": ad.name,
                    "type": "product",
                    "icon": (
                        ad.category.icon.url
                        if ad.category and ad.category.icon
                        else None
                    ),
                }
            )

        return results

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AutoCompleteSearchView(generics.ListAPIView):
    serializer_class = AutoCompleteSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()
        if not query:
            return []

        results = []

        ads = Ad.objects.filter(
            Q(name__icontains=query) & Q(status="active")
        ).select_related("category")[:10]

        for ad in ads:
            results.append(
                {
                    "id": ad.id,
                    "name": ad.name,
                    "icon": (
                        ad.category.icon.url
                        if ad.category and ad.category.icon
                        else None
                    ),
                }
            )

        return results

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PopularSearchView(generics.ListAPIView):
    queryset = PopularSearch.objects.filter(is_active=True)
    serializer_class = PopularSearchSerializer
    pagination_class = StandardResultsSetPagination


@api_view(["GET"])
def search_count_increase(request, id):
    try:
        category = Category.objects.get(id=id)
        search_count, created = SearchCount.objects.get_or_create(
            category=category, defaults={"search_count": 0}
        )
        search_count.increment()

        serializer = SearchCountSerializer(search_count)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response(
            {"error": "Kategoriya topilmadi"}, status=status.HTTP_404_NOT_FOUND
        )
