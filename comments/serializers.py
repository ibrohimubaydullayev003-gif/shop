
from rest_framework import serializers

from .models import Comment
from products.models import Product


class CommentReadSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(
        source="product.id",
        read_only=True
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    user_id = serializers.UUIDField(
        source="user.id",
        read_only=True
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "product_id",
            "product_name",
            "user_id",
            "username",
            "text",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommentCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )

    text = serializers.CharField(max_length=1000)

    rating = serializers.IntegerField(
        min_value=1,
        max_value=5
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "product",
            "text",
            "rating",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context.get("request")
        product = attrs["product"]

        if request and request.user.is_authenticated:
            exists = Comment.objects.filter(
                product=product,
                user=request.user,
            ).exists()

            if exists:
                raise serializers.ValidationError({
                    "detail": (
                        "Siz bu mahsulotga oldin izoh yozgansiz."
                    )
                })

        return attrs


class CommentUpdateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1000)

    rating = serializers.IntegerField(
        min_value=1,
        max_value=5
    )

    class Meta:
        model = Comment
        fields = ["text", "rating"]
