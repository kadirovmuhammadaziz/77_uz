from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category,
    Ad,
    AdPhoto,
    FavoriteProduct,
    SavedSearch,
    SearchCount,
    PopularSearch,
)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "parent",
            "is_active",
            "order",
            "product_count",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["slug", "created_time", "updated_time", "product_count"]


class CategoryWithChildrenSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "parent",
            "is_active",
            "order",
            "product_count",
            "children",
            "created_time",
            "updated_time",
        ]
        read_only_fields = [
            "slug",
            "created_time",
            "updated_time",
            "product_count",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by("order", "name")
        return CategorySerializer(children, many=True, context=self.context).data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone_number"]
        read_only_fields = ["id"]


class SellerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "phone_number", "profile_photo"]
        read_only_fields = ["id", "full_name"]

    def get_full_name(self, obj):
        return (
            obj.get_full_name()
            if hasattr(obj, "get_full_name")
            else f"{obj.first_name} {obj.last_name}".strip()
        )


class AdPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdPhoto
        fields = ["id", "ad", "image", "is_main", "order", "created_time", "updated_time"]
        read_only_fields = ["created_time", "updated_time"]


class AdListSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    seller = SellerSerializer(read_only=True)
    address = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "photo",
            "published_at",
            "address",
            "seller",
            "is_liked",
            "view_count",
            "status",
            "updated_time",
        ]
        read_only_fields = [
            "slug",
            "published_at",
            "view_count",
            "is_liked",
            "photo",
            "address",
            "updated_time",
        ]

    def get_photo(self, obj):
        main_photo = obj.main_photo
        if main_photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(main_photo.url)
            return main_photo.url
        return None

    def get_address(self, obj):
        address_parts = []
        if obj.region:
            address_parts.append(obj.region.name)
        if obj.district:
            address_parts.append(obj.district.name)
        if obj.address:
            address_parts.append(obj.address)
        return ", ".join(address_parts)

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class AdDetailSerializer(serializers.ModelSerializer):
    photos = AdPhotoSerializer(many=True, read_only=True)
    seller = SellerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    address = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "seller",
            "region",
            "district",
            "address",
            "status",
            "is_top",
            "view_count",
            "published_at",
            "photos",
            "is_liked",
            "updated_time",
        ]
        read_only_fields = [
            "slug",
            "published_at",
            "view_count",
            "is_liked",
            "photos",
            "address",
            "updated_time",
        ]

    def get_address(self, obj):
        address_parts = []
        if obj.region:
            address_parts.append(obj.region.name)
        if obj.district:
            address_parts.append(obj.district.name)
        if obj.address:
            address_parts.append(obj.address)
        return ", ".join(address_parts)

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False,
        help_text="Rasm URL'lari ro'yxati",
    )

    class Meta:
        model = Ad
        fields = [
            "id",
            "name",
            "description",
            "category",
            "price",
            "region",
            "district",
            "address",
            "photos",
            "status",

        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        photos_data = validated_data.pop("photos", [])
        validated_data["seller"] = self.context["request"].user
        ad = Ad.objects.create(**validated_data)

        for i, photo_url in enumerate(photos_data):
            AdPhoto.objects.create(ad=ad, image=photo_url, is_main=(i == 0), order=i)

        return ad

    def update(self, instance, validated_data):
        photos_data = validated_data.pop("photos", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if photos_data is not None:
            instance.photos.all().delete()
            for i, photo_url in enumerate(photos_data):
                AdPhoto.objects.create(
                    ad=instance, image=photo_url, is_main=(i == 0), order=i
                )

        return instance


class FavoriteProductSerializer(serializers.ModelSerializer):
    product = AdListSerializer(source="ad", read_only=True)
    ad = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all(), write_only=True)

    class Meta:
        model = FavoriteProduct
        fields = [
            "id",
            "user",
            "ad",
            "product",
            "device_id",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "user", "created_time", "updated_time", "product"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)


class SavedSearchSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = SavedSearch
        fields = [
            "id",
            "user",
            "category",
            "category_id",
            "region",
            "search_query",
            "price_min",
            "price_max",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "user", "created_time", "updated_time"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class SearchCountSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = SearchCount
        fields = ["id", "category", "search_count", "created_time", "updated_time"]
        read_only_fields = ["id", "created_time", "updated_time"]


class PopularSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopularSearch
        fields = [
            "id",
            "name",
            "icon",
            "search_count",
            "is_active",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "created_time", "updated_time"]


class AdPhotoCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AdPhoto
        fields = ["id", "image", "is_main", "product_id", "order", "created_time"]
        read_only_fields = ["id", "created_time"]

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        try:
            ad = Ad.objects.get(id=product_id)
            validated_data["ad"] = ad
        except Ad.DoesNotExist:
            raise serializers.ValidationError({"product_id": "E'lon topilmadi"})

        return super().create(validated_data)


class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()
    icon = serializers.URLField(required=False)


class AutoCompleteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    icon = serializers.URLField(required=False)