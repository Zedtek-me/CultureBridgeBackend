from apps.users.models import User
import logging
from django.utils.functional import SimpleLazyObject
from django.core.exceptions import MiddlewareNotUsed


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UserInjectionMiddleware:
    """injects the user object to the request with the user id if it exists"""
    def __init__(self, get_response):
        self.get_response = get_response
        #set it to unused for now,
        # since it only captures for Django' HttpRequest obj,
        # but not rest_framwork's Request obj.
        raise MiddlewareNotUsed

    def __call__(self, request):
        user = request.user
        user_id_from_header = request.headers.get("X-User-Id") or request.META.get("X-User-Id")
        if user_id_from_header is not None:
            user = User.objects.filter(id=user_id_from_header).first()
            lazy_user = SimpleLazyObject(lambda: user)
            setattr(request, "user", lazy_user)
            request.user = lazy_user
        return self.get_response(request)
