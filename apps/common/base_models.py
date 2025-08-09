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