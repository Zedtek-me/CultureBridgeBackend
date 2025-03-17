from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from apps.blogs.permissions.is_authenticated import IsAuthenticated
from apps.core.serializers import (
    TrainingSerializer,
    AcceptPaymentSerializer
)

from utils.core_utils import TrainingUtil
from utils.response_utils import ResponseManager


class TrainingViewSet(ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        user = request.user
        trainings = TrainingUtil.list_trainings(
            user, request.query_params
        )
        serializer = TrainingSerializer(trainings, many=True)
        return ResponseManager

    @action(detail=False, methods=["post"], url_path="process-payment")
    def process_training_payment(self, request):
        """processes training payment for user signing up"""
        serializer = AcceptPaymentSerializer(request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_messages,
                status_code=400
            )
        response = TrainingUtil.process_training_payment(**serializer.validated_data, user=request.user)
        if isinstance(response, tuple):
            access_code, _ = response
            return ResponseManager.handle_success_response(
                message="payment initiated successfully!",
                data={"access_code": access_code},
                status_code=200
            )
        return ResponseManager.handle_success_response(
            message="payment initiated successfully!",
            data=response
        )


class Dashboard(ViewSet):

    @action(methods=["get"], detail=False, url_path="dashboard")
    def get_dashboard_data(self, request):
        pass
