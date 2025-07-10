from collections import defaultdict
from itertools import dropwhile

from django.db import models
from django.utils import timzone

class Region(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

class District(models.Model):
    name = models.CharField(max_length=200)
    region = models.ForeingKey(Region,on_delete=models.CASCADE,related_name='districts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "District"
        verbose_name_plural = 'Districts'

class StaticPage(models.Model):
    slug = models.SLugField(unique=True, max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Static Page"
        verbose_name_plural = "Static Pages"


class Setting(models.Model):
    phone = models.CharField(max_length=20,default="+998770367366")
    support_email = models.EmailField(default="support@77.uz")
    working_hours = models.CharField(max_length=200 , default="Dushanba-Yakshanba 9:00=21:00 ")
    maintenance_mode = models.BoolenField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "App Settings"

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
