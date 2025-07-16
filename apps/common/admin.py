from django.contrib import admin
from .models import StaticPage, Region, District, Setting


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name','guid', 'created_at', 'updated_at')
    search_fields = ('name',)
    inlines = [DistrictInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'guid','created_at', 'updated_at')
    list_filter = ('region',)
    search_fields = ('name', 'region__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('phone', 'support_email', 'app_version', 'maintenance_mode', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return not Setting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False