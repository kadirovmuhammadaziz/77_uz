import django_filters
from django import forms
from .models import Ad, Category


class AdFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"placeholder": "Mahsulot nomini kiriting"}),
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        empty_label="Barcha kategoriyalar",
    )

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        widget=forms.NumberInput(attrs={"placeholder": "Min narx"}),
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        widget=forms.NumberInput(attrs={"placeholder": "Max narx"}),
    )

    region = django_filters.CharFilter(
        field_name="region__name",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"placeholder": "Viloyat nomi"}),
    )

    district = django_filters.CharFilter(
        field_name="district__name",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"placeholder": "Tuman nomi"}),
    )

    is_new = django_filters.BooleanFilter(
        field_name="is_new", widget=forms.CheckboxInput()
    )

    is_top = django_filters.BooleanFilter(
        field_name="is_top", widget=forms.CheckboxInput()
    )

    published_after = django_filters.DateFilter(
        field_name="published_at",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    published_before = django_filters.DateFilter(
        field_name="published_at",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Ad
        fields = [
            "name",
            "category",
            "min_price",
            "max_price",
            "region",
            "district",
            "is_new",
            "is_top",
            "published_after",
            "published_before",
        ]
