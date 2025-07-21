from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from common.models import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=200, verbose_name="Nomi")
    slug = models.SlugField(unique=True, blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        verbose_name="Ota kategoriya"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        return self.ads.filter(status='active').count()

    def get_all_children(self):
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children


class Ad(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Faol'),
        ('inactive', 'Nofaol'),
        ('pending', 'Kutilmoqda'),
        ('rejected', 'Rad etilgan'),
    ]

    name = models.CharField(max_length=300, verbose_name="Nomi")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Tavsif")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name="Kategoriya"
    )
    price = models.PositiveBigIntegerField(verbose_name="Narx (so'm)")
    seller = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name="Sotuvchi"
    )

    region = models.ForeignKey(
        'common.Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Viloyat"
    )
    district = models.ForeignKey(
        'common.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tuman"
    )
    address = models.CharField(max_length=500, blank=True, verbose_name="Manzil")

    # Status and visibility
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Holat"
    )
    is_top = models.BooleanField(default=False, verbose_name="Top e'lon")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni")

    published_at = models.DateTimeField(auto_now_add=True, verbose_name="E'lon qilingan vaqt")

    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['is_top', 'published_at']),
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
        return reverse('store:ad_detail', kwargs={'slug': self.slug})

    @property
    def main_photo(self):
        main_photo = self.photos.filter(is_main=True).first()
        return main_photo.image if main_photo else None

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class AdPhoto(BaseModel):
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="E'lon"
    )
    image = models.ImageField(upload_to='ads_photos/', verbose_name="Rasm")
    is_main = models.BooleanField(default=False, verbose_name="Asosiy rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "E'lon rasmi"
        verbose_name_plural = "E'lon rasmlari"
        ordering = ['-is_main', 'order']

    def __str__(self):
        return f"{self.ad.name} - {'Asosiy' if self.is_main else 'Qo\'shimcha'}"

    def save(self, *args, **kwargs):
        if self.is_main:
            AdPhoto.objects.filter(ad=self.ad, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class FavoriteProduct(BaseModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='favorites',
        null=True,
        blank=True,
        verbose_name="Foydalanuvchi"
    )
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="E'lon"
    )
    device_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Qurilma ID",
        help_text="Ro'yxatdan o'tmagan foydalanuvchilar uchun"
    )

    class Meta:
        verbose_name = "Sevimli mahsulot"
        verbose_name_plural = "Sevimli mahsulotlar"
        unique_together = [
            ('user', 'ad'),
            ('device_id', 'ad'),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.ad.name}"
        return f"Device {self.device_id} - {self.ad.name}"


class SavedSearch(BaseModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='saved_searches',
        verbose_name="Foydalanuvchi"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Kategoriya"
    )
    region = models.ForeignKey(
        'common.Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Viloyat"
    )
    search_query = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Qidiruv so'rovi"
    )
    price_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Minimal narx"
    )
    price_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maksimal narx"
    )

    class Meta:
        verbose_name = "Saqlangan qidiruv"
        verbose_name_plural = "Saqlangan qidiruvlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.search_query or 'Qidiruv'}"


class SearchCount(BaseModel):
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name='search_stats',
        verbose_name="Kategoriya"
    )
    search_count = models.PositiveIntegerField(default=0, verbose_name="Qidiruv soni")

    class Meta:
        verbose_name = "Qidiruv statistikasi"
        verbose_name_plural = "Qidiruv statistikalari"
        ordering = ['-search_count']

    def __str__(self):
        return f"{self.category.name} - {self.search_count}"

    def increment(self):
        self.search_count += 1
        self.save(update_fields=['search_count'])


class PopularSearch(BaseModel):
    name = models.CharField(max_length=200, unique=True, verbose_name="Nomi")
    icon = models.ImageField(
        upload_to='search_icons/',
        blank=True,
        null=True,
        verbose_name="Ikonka"
    )
    search_count = models.PositiveIntegerField(default=0, verbose_name="Qidiruv soni")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Mashhur qidiruv"
        verbose_name_plural = "Mashhur qidiruvlar"
        ordering = ['-search_count']

    def __str__(self):
        return self.name

    def increment(self):
        self.search_count += 1
        self.save(update_fields=['search_count'])

