
from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating",
        "created_at",
    ]

    search_fields = [
        "product__name",
        "user__username",
        "text",
    ]

    list_filter = ["rating", "created_at"]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
