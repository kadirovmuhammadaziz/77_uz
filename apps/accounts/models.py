from collections import defaultdict

from django.contrib.auth.models import AbsracrUser
from django.db import models
from django.core.validators import RegexValidator

class Address(models.Model):
    name = models.CharField(max_length=500)
    lat = models.DecimalField(max_digiths=10,decimal_places=8)
    long = models.DecimalField(max_digits=11,decimal_places=8)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None  # Remove username field
    phone_regex = RegexValidator(
        regex=r'^\+998\d{9}$',
        message="Phone number must be in format: +998XXXXXXXXX"
    )

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        unique=True
    )
    profile_photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(balnk=True)

    def __str__(self):
        return self.name

class SellerRegistration(models.Model):
    STATUS_CHOICE =[
        ('pending','Pending'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ]

    full_name = models.CharField(max_length=255)
    project_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category,on_delete=models.CASCAD)
    phone_number = models.CharField(max_length=13)
    address= models.TextField()
    statistics = models.CharField(
        max_length=100,
        choices=STATUS_CHOICE,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name}-{self.full_name}"
