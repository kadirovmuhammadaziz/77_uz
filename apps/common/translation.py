from modeltranslation.translator import register, TranslationOptions
from .models import Region, District, Setting, StaticPage


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(District)
class DistrictTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Setting)
class SettingTranslationOptions(TranslationOptions):
    fields = ("working_hours",)


@register(StaticPage)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "content")
