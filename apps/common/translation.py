from modeltranslation.translator import translator, TranslationOptions
from .models import Region, District, StaticPage, Setting


class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


class DistrictTranslationOptions(TranslationOptions):
    fields = ('name',)


class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'meta_description')


class SettingTranslationOptions(TranslationOptions):
    fields = ('working_hours', 'app_name')