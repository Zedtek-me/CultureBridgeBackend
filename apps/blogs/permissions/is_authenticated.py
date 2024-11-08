from rest_framework.permissions import BasePermission

from apps.users.models import User
import logging

logger = logging.getLogger("root")


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        user_id_from_header = request.headers.get("X-User-Id") #or request.META.get("X-User-Id")
        logger.debug(f"user_id_from_header:::: {user_id_from_header}")
        if user_id_from_header:
            user = User.objects.filter(id=user_id_from_header).first()
            request.user = user
            return True
        return user.is_authenticated


class AllowByPass(BasePermission):
    def has_permission(self, request, view):
        by_pass_header = request.headers.get("X-By-Pass")
        if by_pass_header:
            return True
        return False
