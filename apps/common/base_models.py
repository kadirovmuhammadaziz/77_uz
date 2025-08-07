import uuid
from django.db import models


class BaseModel(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_time = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaratilgan vaqti"
    )
    updated_time = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.__class__.__name__} - {self.guid}"


class BaseModelWithSlug(BaseModel):
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL nomi")

    class Meta:
        abstract = True


class BaseModelWithStatus(BaseModel):
    """Status maydoni bilan base model"""

    STATUS_CHOICES = [
        ("active", "Faol"),
        ("inactive", "Nofaol"),
        ("draft", "Qoralama"),
        ("archived", "Arxivlangan"),
    ]

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="Holati"
    )

    class Meta:
        abstract = True
