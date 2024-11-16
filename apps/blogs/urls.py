from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.blogs.views import BlogViewSet, VlogViewSet

router = DefaultRouter(trailing_slash=False)
router.register("blogs", BlogViewSet, basename="blogs")
router.register("vlogs", VlogViewSet, basename="vlogs")


urlpatterns = [
    path("", include(router.urls))
]
