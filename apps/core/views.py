import logging

from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from django.db.models import Q
from django.db import transaction

from apps.blogs.permissions.is_authenticated import IsAuthenticated
from apps.core.serializers import (
    TrainingSerializer,
    AcceptPaymentSerializer
)

from utils.core_utils import TrainingUtil
from utils.response_utils import ResponseManager
from utils.validators import format_date
from utils.helpers import paginate_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TrainingViewSet(ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        user = request.user
        params = request.query_params
        filters = {}
        page_count = params.get("page_count") or 10
        page_no = params.get("page_no") or 1
        search_filter = Q()
        if params.get("assigned_to_me"):
            filters["instructor_id"] = user.id
        if params.get("search"):
            search_txt = params.get("search")
            search_filter = (
                Q(status__iexact=search_txt) |
                Q(language__icontains=search_txt) |
                Q(payment_status__iexact=search_txt)
            )
        if params.get("instructor_id"):
            filters["instructor_id"] = params.get("instructor_id")
        if params.get("start_date") and params.get("end_date"):
            start_date = format_date(params.get("start_date", ""))
            end_date = format_date(params.get("end_date", ""))
            filters.update({"start_date": start_date, "end_date": end_date})
        if params.get("start_date") and not params.get("end_date"):
            start_date = format_date(params.get("start_date"))
            filters.update({"start_date": start_date})
        if params.get("end_date") and not params.get("start_date"):
            end_date = format_date(params.get("end_date"))
            filters.update({"end_date": end_date})
        trainings = TrainingUtil.list_trainings(search_filter, filters, user=user, paginate=False)
        serializer = TrainingSerializer(trainings, many=True)
        paginated_data = paginate_data(serializer.data, page_count, page_no)
        data_fmt = {"traingings": paginated_data.get("data"), **paginated_data}
        del data_fmt["data"]
        return ResponseManager.handle_success_response(
            message="trainings successfully fetched!",
            data=data_fmt
        )

    def retrieve(self, request, pk = None):
        user = request.user
        params = request.query_params
        filters = {"id": pk}
        search_filter = Q()
        if params.get("assigned_to_me"):
            filters["instructor_id"] = user.id
        if params.get("search"):
            search_txt = params.get("search")
            search_filter = (
                Q(status__iexact=search_txt) |
                Q(language__icontains=search_txt) |
                Q(payment_status__iexact=search_txt)
            )
        if params.get("instructor_id"):
            filters["instructor_id"] = params.get("instructor_id")
        if params.get("start_date") or params.get("end_date"):
            start_date = format_date(params.get("start_date", ""))
            end_date = format_date(params.get("end_date", ""))
            filters.update({"start_date": start_date, "end_date": end_date})
        training = TrainingUtil.get_training(search_filter, filters)
        serializer = TrainingSerializer(training)
        return ResponseManager.handle_success_response(
            message="training successfully retrieved!", data=serializer.data
        )

    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="process-payment")
    def process_training_payment(self, request):
        """processes training payment for user signing up"""
        serializer = AcceptPaymentSerializer(data=request.data)
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
        """gets the dashboard data based on the user profile type"""
        pass
