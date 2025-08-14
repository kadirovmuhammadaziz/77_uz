from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User, Address
from store.models import Category


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("phone_number", "full_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "phone_number",
            "full_name",
            "password",
            "is_active",
            "is_staff",
            "role",
            "status",
            "profile_photo",
            "project_name",
            "category",
        )

    def clean_password(self):
        return self.initial["password"]


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    readonly_fields = ("name", "lat", "long")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    inlines = [AddressInline]

    list_display = (
        "id",
        "phone_number",
        "full_name",
        "role",
        "status",
        "is_active",
        "is_staff",
        "created_time",
    )
    list_filter = ("role", "status", "is_active", "is_staff", "created_time")
    search_fields = ("phone_number", "full_name", "project_name")
    ordering = ("-created_time",)

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal Info", {"fields": ("full_name", "profile_photo")}),
        ("Seller Info", {"fields": ("project_name", "category")}),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "status",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "created_time", "updated_time")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "full_name", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ("created_time", "updated_time")

    actions = ["approve_sellers", "reject_sellers"]

    def approve_sellers(self, request, queryset):
        sellers = queryset.filter(role="seller", status="pending")
        count = sellers.update(status="approved", is_active=True)
        self.message_user(request, f"{count} seller(s) successfully approved.")

    approve_sellers.short_description = "Approve selected sellers"

    def reject_sellers(self, request, queryset):
        sellers = queryset.filter(role="seller", status="pending")
        count = sellers.update(status="rejected", is_active=False)
        self.message_user(request, f"{count} seller(s) rejected.")

    reject_sellers.short_description = "Reject selected sellers"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "lat", "long")
    search_fields = ("user__full_name", "name")
