from django.contrib import admin
from .models import Region, District, StaticPage, Setting


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_time', 'updated_time')
    search_fields = ('name',)
    readonly_fields = ('guid', 'created_time', 'updated_time')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'created_time', 'updated_time')
    list_filter = ('region', 'created_time')
    search_fields = ('name', 'region__name')
    readonly_fields = ('guid', 'created_time', 'updated_time')


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_time', 'updated_time')
    list_filter = ('is_active', 'created_time')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('guid', 'created_time', 'updated_time')


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'phone', 'support_email', 'maintenance_mode')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Settings', {
            'fields': ('app_name', 'app_logo', 'maintenance_mode')
        }),
        ('Contact Information', {
            'fields': ('phone', 'support_email', 'working_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'telegram_url')
        }),
        ('Legal', {
            'fields': ('privacy_policy_url', 'terms_of_service_url')
        }),
        ('Delivery', {
            'fields': ('delivery_fee', 'free_delivery_minimum')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        return not Setting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
