from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, MailingViewSet
from apps.users.auth_views import AuthViewSet
router = DefaultRouter(trailing_slash=False)
router.register("users", UserViewSet, basename="users")
router.register("mailing", MailingViewSet, basename="mailing")
router.register("auth", AuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls))
]
