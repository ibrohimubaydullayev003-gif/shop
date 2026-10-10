
from django.db.models import Avg, Count, Q

from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import ProductPermission
from .filters import ProductFilter

from comments.models import Comment
from comments.serializers import (
    CommentReadSerializer,
    CommentCreateSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(
        is_active=True
    ).order_by("name")

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [ProductPermission]

    filterset_class = ProductFilter
    filter_backends = [
        __import__(
            "django_filters.rest_framework",
            fromlist=["DjangoFilterBackend"]
        ).DjangoFilterBackend,
        __import__(
            "rest_framework.filters",
            fromlist=["SearchFilter"]
        ).SearchFilter,
        __import__(
            "rest_framework.filters",
            fromlist=["OrderingFilter"]
        ).OrderingFilter,
    ]

    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Product.objects.select_related(
            "category", "seller"
        ).annotate(
            avg_rating=Avg("comments__rating"),
            comments_count=Count("comments", distinct=True),
        )

        user = self.request.user

        # Administrator barcha mahsulotlarni ko'radi
        if user.is_authenticated and user.is_staff:
            return queryset

        # Sotuvchi faol mahsulotlar va o'z mahsulotlarini ko'radi
        if (
            user.is_authenticated
            and getattr(user, "user_role", None) == "seller"
        ):
            return queryset.filter(
                Q(is_active=True) | Q(seller=user)
            ).distinct()

        # Boshqa foydalanuvchilar faqat faol mahsulotlarni ko'radi
        return queryset.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return ProductWriteSerializer

        return ProductReadSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="comments",
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def comments(self, request, pk=None):
        product = self.get_object()

        if request.method == "GET":
            comments = product.comments.select_related(
                "user", "product"
            ).all()

            serializer = CommentReadSerializer(
                comments,
                many=True,
                context=self.get_serializer_context(),
            )

            return Response(serializer.data)

        # POST so'rovida mahsulot ID sini avtomatik biriktiramiz
        data = request.data.copy()
        data["product"] = str(product.id)

        serializer = CommentCreateSerializer(
            data=data,
            context=self.get_serializer_context(),
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        result = CommentReadSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )

        return Response(
            result.data,
            status=status.HTTP_201_CREATED,
        )
