from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from common.base_models import BaseModel
from .managers import UserManager


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+998\d{9}$',
        message="Phone number must be in format: +998XXXXXXXXX"
    )

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[phone_regex]
    )
    profile_photo = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )

    project_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Required for sellers"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='sellers',
        null=True,
        blank=True,
        help_text="Required for sellers"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'  # Default customer
    )
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default='pending'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    def save(self, *args, **kwargs):
        if self.role == 'seller' and self.status == 'pending':
            self.is_active = False
        elif self.status == 'approved':
            self.is_active = True
        super().save(*args, **kwargs)

    @property
    def is_seller(self):
        return self.role == 'seller'

    @property
    def is_customer(self):
        return self.role == 'customer'


class Address(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='address'
    )
    name = models.TextField()
    lat = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        help_text="Latitude coordinate"
    )
    long = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        help_text="Longitude coordinate"
    )

    def __str__(self):
        return f"{self.name} - {self.user.full_name}"



class SellerRegistrationRequest(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registration_requests'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_registrations'
    )
    processed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"Registration request - {self.user.full_name}"