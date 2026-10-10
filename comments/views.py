
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Comment
from .serializers import (
    CommentReadSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from .permissions import CommentPermission


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [CommentPermission]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = ["product", "rating"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "product", "user"
        )

        # Administrator faol bo'lmagan mahsulot izohlarini ham ko'radi
        if not (
            self.request.user.is_authenticated
            and self.request.user.is_staff
        ):
            queryset = queryset.filter(product__is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer

        if self.action in ["update", "partial_update"]:
            return CommentUpdateSerializer

        return CommentReadSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
