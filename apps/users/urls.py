from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, MailingViewSet
router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("mailing", MailingViewSet, basename="mailing")

urlpatterns = [
    path("v1/", include(router.urls))
]
