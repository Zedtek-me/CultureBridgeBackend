from django.urls import path, include

from rest_framework.routers import DefaultRouter
from apps.core.views import TrainingViewSet, DashboardViewSet



router = DefaultRouter(trailing_slash=False)

router.register('training', TrainingViewSet, basename='training')
router.register("dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = [
    path('', include(router.urls))
]
