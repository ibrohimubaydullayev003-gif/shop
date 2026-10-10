
from django_filters import rest_framework as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name="category__slug",
        lookup_expr="iexact"
    )

    min_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    max_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "min_price",
            "max_price",
        ]
