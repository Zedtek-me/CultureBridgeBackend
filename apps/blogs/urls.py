from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path("", router.urls)
]
