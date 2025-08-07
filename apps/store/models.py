from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from common.base_models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=200, verbose_name="Name")
    slug = models.SlugField(unique=True, blank=True)
    icon = models.ImageField(upload_to="category_icons/", blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        verbose_name="Parent category",
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        return self.ads.filter(status="active").count()

    def get_all_children(self):
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children


class Ad(BaseModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
        ("rejected", "Rejected"),
    ]

    name = models.CharField(max_length=300, verbose_name="Name")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Category",
    )
    price = models.PositiveBigIntegerField(verbose_name="Price (UZS)")
    seller = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Seller",
    )

    region = models.ForeignKey(
        "common.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Region",
    )
    district = models.ForeignKey(
        "common.District",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="District",
    )
    address = models.CharField(max_length=500, blank=True, verbose_name="Address")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Status"
    )
    is_top = models.BooleanField(default=False, verbose_name="Top ad")
    view_count = models.PositiveIntegerField(default=0, verbose_name="View count")

    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Published at")

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["seller", "status"]),
            models.Index(fields=["price"]),
            models.Index(fields=["is_top", "published_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1

        while Ad.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def get_absolute_url(self):
        return reverse("store:ad_detail", kwargs={"slug": self.slug})

    @property
    def main_photo(self):
        main_photo = self.photos.filter(is_main=True).first()
        return main_photo.image if main_photo else None

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])


class AdPhoto(BaseModel):
    ad = models.ForeignKey(
        Ad, on_delete=models.CASCADE, related_name="photos", verbose_name="Ad"
    )
    image = models.ImageField(upload_to="ads_photos/", verbose_name="Image")
    is_main = models.BooleanField(default=False, verbose_name="Main image")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")

    class Meta:
        verbose_name = "Ad photo"
        verbose_name_plural = "Ad photos"
        ordering = ["-is_main", "order"]

    def __str__(self):
        return f"{self.ad.name} - {'Main' if self.is_main else 'Additional'}"

    def save(self, *args, **kwargs):
        if self.is_main:
            AdPhoto.objects.filter(ad=self.ad, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class FavoriteProduct(BaseModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="favorites",
        null=True,
        blank=True,
        verbose_name="User",
    )
    ad = models.ForeignKey(
        Ad, on_delete=models.CASCADE, related_name="favorited_by", verbose_name="Ad"
    )
    device_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Device ID",
        help_text="For unauthenticated users",
    )

    class Meta:
        verbose_name = "Favorite product"
        verbose_name_plural = "Favorite products"
        unique_together = [
            ("user", "ad"),
            ("device_id", "ad"),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.ad.name}"
        return f"Device {self.device_id} - {self.ad.name}"


class SavedSearch(BaseModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="saved_searches",
        verbose_name="User",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Category",
    )
    region = models.ForeignKey(
        "common.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Region",
    )
    search_query = models.CharField(
        max_length=200, blank=True, verbose_name="Search query"
    )
    price_min = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Min price"
    )
    price_max = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Max price"
    )

    class Meta:
        verbose_name = "Saved search"
        verbose_name_plural = "Saved searches"
        ordering = ["-created_time"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.search_query or 'Search'}"


class SearchCount(BaseModel):
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="search_stats",
        verbose_name="Category",
    )
    search_count = models.PositiveIntegerField(default=0, verbose_name="Search count")

    class Meta:
        verbose_name = "Search statistic"
        verbose_name_plural = "Search statistics"
        ordering = ["-search_count"]

    def __str__(self):
        return f"{self.category.name} - {self.search_count}"

    def increment(self):
        self.search_count += 1
        self.save(update_fields=["search_count"])


class PopularSearch(BaseModel):
    name = models.CharField(max_length=200, unique=True, verbose_name="Name")
    icon = models.ImageField(
        upload_to="search_icons/", blank=True, null=True, verbose_name="Icon"
    )
    search_count = models.PositiveIntegerField(default=0, verbose_name="Search count")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Popular search"
        verbose_name_plural = "Popular searches"
        ordering = ["-search_count"]

    def __str__(self):
        return self.name

    def increment(self):
        self.search_count += 1
        self.save(update_fields=["search_count"])
