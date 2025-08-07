# store/admin.py
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin
from .models import (
    Category,
    Ad,
    AdPhoto,
    FavoriteProduct,
    SavedSearch,
    SearchCount,
    PopularSearch,
)


class AdPhotoInline(admin.TabularInline):
    model = AdPhoto
    extra = 1
    fields = ("image", "is_main", "order")


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ["name", "parent", "product_count", "is_active", "order"]
    list_filter = ["is_active", "parent", "created_time"]
    search_fields = ["name_uz", "name_ru"]
    prepopulated_fields = {"slug": ("name_uz",)}
    ordering = ["order", "name"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")


@admin.register(Ad)
class AdAdmin(TranslationAdmin):
    list_display = [
        "name",
        "category",
        "seller",
        "price_formatted",
        "status",
        "is_top",
        "view_count",
        "published_at",
    ]
    list_filter = [
        "status",
        "is_top",
        "category",
        "region",
        "published_at",
        "created_time",
    ]
    search_fields = [
        "seller__first_name",
        "seller__last_name",
        "seller__phone",
    ]
    prepopulated_fields = {"slug": ("name_uz",)}
    inlines = [AdPhotoInline]
    date_hierarchy = "published_at"

    readonly_fields = ["slug", "view_count", "published_at"]

    fieldsets = (
        (
            "Asosiy ma'lumotlar",
            {
                "fields": (
                    "name_uz",
                    "name_ru",
                    "slug",
                    "category",
                    "description_uz",
                    "description_ru",
                )
            },
        ),
        ("Narx va joylashuv", {"fields": ("price", "region", "district", "address")}),
        ("Sotuvchi", {"fields": ("seller",)}),
        ("Holat va sozlamalar", {"fields": ("status", "is_top")}),
        (
            "Statistika",
            {"fields": ("view_count", "published_at"), "classes": ("collapse",)},
        ),
    )

    def price_formatted(self, obj):
        return f"{obj.price:,} so'm"

    price_formatted.short_description = "Narx"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category", "seller", "region", "district")
        )

    actions = ["make_active", "make_inactive", "make_top"]

    def make_active(self, request, queryset):
        updated = queryset.update(status="active")
        self.message_user(request, f"{updated} ta e'lon faollashtirildi.")

    make_active.short_description = "Tanlangan e'lonlarni faollashtirish"

    def make_inactive(self, request, queryset):
        updated = queryset.update(status="inactive")
        self.message_user(request, f"{updated} ta e'lon nofaol qilindi.")

    make_inactive.short_description = "Tanlangan e'lonlarni nofaol qilish"

    def make_top(self, request, queryset):
        updated = queryset.update(is_top=True)
        self.message_user(request, f"{updated} ta e'lon top qilindi.")

    make_top.short_description = "Tanlangan e'lonlarni top qilish"


@admin.register(AdPhoto)
class AdPhotoAdmin(admin.ModelAdmin):
    list_display = ["ad", "image_preview", "is_main", "order"]
    list_filter = ["is_main", "created_time"]
    search_fields = ["ad__name_uz", "ad__name_ru"]
    ordering = ["ad", "-is_main", "order"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;">',
                obj.image.url,
            )
        return "Rasm yo'q"

    image_preview.short_description = "Rasm"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("ad")


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ["user_or_device", "ad", "created_time"]
    list_filter = ["created_time"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone",
        "device_id",
        "ad__name_uz",
        "ad__name_ru",
    ]

    def user_or_device(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return f"Device: {obj.device_id}"

    user_or_device.short_description = "Foydalanuvchi"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "ad")


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "search_query",
        "category",
        "region",
        "price_range",
        "created_time",
    ]
    list_filter = ["category", "region", "created_time"]
    search_fields = ["user__first_name", "user__last_name", "search_query"]

    def price_range(self, obj):
        if obj.price_min and obj.price_max:
            return f"{obj.price_min:,} - {obj.price_max:,}"
        elif obj.price_min:
            return f"From {obj.price_min:,}"
        elif obj.price_max:
            return f"Up to {obj.price_max:,}"
        return "No price limit"

    price_range.short_description = "Narx oralig'i"

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("user", "category", "region")
        )


@admin.register(SearchCount)
class SearchCountAdmin(admin.ModelAdmin):
    list_display = ["category", "search_count", "updated_time"]
    list_filter = ["updated_time"]
    search_fields = ["category__name_uz", "category__name_ru"]
    ordering = ["-search_count"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")


@admin.register(PopularSearch)
class PopularSearchAdmin(TranslationAdmin):
    list_display = ["name", "search_count", "is_active", "updated_time"]
    list_filter = ["is_active", "updated_time"]
    search_fields = ["name_uz", "name_ru"]
    ordering = ["-search_count"]

    actions = ["make_active", "make_inactive"]

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} ta qidiruv faollashtirildi.")

    make_active.short_description = "Tanlangan qidiruvlarni faollashtirish"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta qidiruv nofaol qilindi.")

    make_inactive.short_description = "Tanlangan qidiruvlarni nofaol qilish"
