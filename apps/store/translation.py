from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Ad, PopularSearch


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('uz', 'ru')

translator.register(Category, CategoryTranslationOptions)


class AdTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    required_languages = ('uz', 'ru')

translator.register(Ad, AdTranslationOptions)


class PopularSearchTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('uz', 'ru')

translator.register(PopularSearch, PopularSearchTranslationOptions)