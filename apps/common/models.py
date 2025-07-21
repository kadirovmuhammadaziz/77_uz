from django.db import models
from .base_models import BaseModel



class Region(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(BaseModel):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='districts'
    )

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ['name']
        unique_together = ['name', 'region']

    def __str__(self):
        return f"{self.name} - {self.region.name}"


class StaticPage(BaseModel):
    slug = models.SlugField(unique=True, max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "Static Page"
        verbose_name_plural = "Static Pages"
        ordering = ['title']

    def __str__(self):
        return self.title


class Setting(models.Model):
    phone = models.CharField(max_length=20, default="+998770367366")
    support_email = models.EmailField(default="support@77.uz")
    working_hours = models.CharField(
        max_length=200,
        default="Dushanba-Yakshanba 9:00-21:00"
    )
    maintenance_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    app_name = models.CharField(max_length=100, default="77.uz")
    app_logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    privacy_policy_url = models.URLField(blank=True)
    terms_of_service_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    free_delivery_minimum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

    def __str__(self):
        return "App Settings"

    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            raise ValueError("Only one Settings instance is allowed")
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings