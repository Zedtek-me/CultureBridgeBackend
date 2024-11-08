from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.blogs.views import BlogViewSet

router = DefaultRouter()
router.register("blogs", BlogViewSet, basename="blogs")

urlpatterns = [
    path("", include(router.urls))
]
