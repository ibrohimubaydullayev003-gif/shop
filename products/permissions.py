
from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import SELLER


class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS: mahsulotlarni ko'rish
        if request.method in SAFE_METHODS:
            return True

        # Boshqa amallar uchun login talab qilinadi
        if not request.user.is_authenticated:
            return False

        # Mahsulot yaratish: sotuvchi yoki administrator
        if view.action == "create":
            return (
                request.user.is_staff
                or getattr(request.user, "user_role", None) == SELLER
            )

        return True

    def has_object_permission(self, request, view, obj):
        # Mahsulotlarni ko'rish hammaga mumkin
        if request.method in SAFE_METHODS:
            return True

        # Sotuvchi faqat o'z mahsulotini boshqaradi
        return (
            request.user.is_staff
            or obj.seller_id == request.user.id
        )
