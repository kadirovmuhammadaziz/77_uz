import uuid
from django.db import models
class BaseModel(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True