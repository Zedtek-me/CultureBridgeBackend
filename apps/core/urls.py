from django.urls import path, include

from rest_framework.routers import DefaultRouter
from apps.core.views import TrainingViewSet



router = DefaultRouter(trailing_slash=False)

router.register('training', TrainingViewSet, basename='training')

urlpatterns = [
    path('', include(router.urls))
]
