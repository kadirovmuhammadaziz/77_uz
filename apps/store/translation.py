from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Ad, PopularSearch


class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Category, CategoryTranslationOptions)


class AdTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Ad, AdTranslationOptions)


class PopularSearchTranslationOptions(TranslationOptions):
    fields = ("name",)

translator.register(PopularSearch, PopularSearchTranslationOptions)
