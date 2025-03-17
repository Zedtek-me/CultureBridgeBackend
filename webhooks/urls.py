from rest_framework.routers import DefaultRouter
from django.urls import path, include

from webhooks.paystack.transactions import TransactionHooks as PayStackTxnHookViewSet

router = DefaultRouter(trailing_slash=False)
router.register("webhooks/paystack", PayStackTxnHookViewSet, basename="paystack_webhooks")

urlpatterns = [
    path("", include(router.urls))
]
