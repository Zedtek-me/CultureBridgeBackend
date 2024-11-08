from apps.users.models import User
import logging
from django.utils.functional import SimpleLazyObject


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UserInjectionMiddleware:
    """injects the user object to the request with the user id if it exists"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        user_id_from_header = request.headers.get("X-User-Id") or request.META.get("X-User-Id")
        logger.debug(f"user_id_from_header:::: {user_id_from_header}\n user obj from request: {user}")
        if user_id_from_header is not None:
            user = User.objects.filter(id=user_id_from_header).first()
            lazy_user = SimpleLazyObject(lambda: user)
            setattr(request, "user", lazy_user)
        logger.debug(f"current user from request after if check:::: {request.user}")
        return self.get_response(request)
