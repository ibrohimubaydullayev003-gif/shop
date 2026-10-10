
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    category_id = serializers.UUIDField(
        source="category.id",
        read_only=True
    )

    seller_id = serializers.UUIDField(
        source="seller.id",
        read_only=True
    )

    seller_username = serializers.CharField(
        source="seller.username",
        read_only=True
    )

    average_rating = serializers.SerializerMethodField()

    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_id",
            "seller_id",
            "seller_username",
            "price",
            "stock",
            "image",
            "is_active",
            "average_rating",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_average_rating(self, obj):
        average = getattr(obj, "avg_rating", None)

        if average is None:
            return 0.0

        return round(float(average), 1)


class ProductWriteSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True)
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "price",
            "stock",
            "image",
            "is_active",
        ]
        read_only_fields = ["id"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Mahsulot narxi noldan katta bo'lishi kerak."
            )

        return value
