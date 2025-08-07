from django.db import models
from .base_models import BaseModel


class Region(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(BaseModel):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "region"]

    def __str__(self):
        return f"{self.name} - {self.region.name}"


class StaticPage(BaseModel):
    slug = models.SlugField(unique=True, max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Setting(BaseModel):
    phone = models.CharField(max_length=20, default="+998770367366")
    support_email = models.EmailField(default="support@77.uz")
    working_hours = models.CharField(max_length=200, default="Monday-Sunday 9:00-21:00")
    maintenance_mode = models.BooleanField(default=True)

    def __str__(self):
        return "App Settings"

    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            raise ValueError("Only one Settings instance is allowed")
        super().save(*args, **kwargs),

        @classmethod
        def get_settings(cls):
            settings, created = cls.objects.get_or_create(pk=1)
            return settings

    class Meta:
        ordering = ["-created_time"]
