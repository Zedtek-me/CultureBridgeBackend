import logging

from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Q
from django.db import transaction

from apps.blogs.permissions.is_authenticated import IsAuthenticated
from apps.core.serializers import (
    TrainingSerializer,
    AcceptPaymentSerializer, ConfirmPaymentSerializer,
    TrainingMetrics, CourseSerializer,
    AssignCourseSerializer, AssignmentSerializer,
    MarkAttendanceSerializer, CreateAssignmentSerializer,
    UpdateAssignmentSerializer, CreateCourseSerializer
)

from apps.core.models  import TrainingCourse

from utils.core_utils import TrainingUtil, DashboardUtil
from utils.http_utils import ResponseManager
from utils.user_utils import UserUtils
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
        filters = {"user__id": user.id}
        page_count = params.get("page_count") or 10
        page_no = params.get("page_no") or 1
        search_filter = Q()
        if params.get("assigned_to_me"):
            filters.pop("user__id", None)
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
        data: dict = serializer.validated_data
        data.update(option=data.pop("payment_option", "card"))
        logger.debug(f"payment data:::: {data}")
        response = TrainingUtil.process_training_payment(**data, user=request.user)
        if isinstance(response, tuple):
            access_code, _ = response
            return ResponseManager.handle_success_response(
                message="payment initiated successfully!",
                data={"access_code": access_code},
                status_code=200
            )
        if not response.get("success"):
            msg = response.get("message", "Unable to process payment at the moment!")
            return ResponseManager.handle_error_response(
                message=msg,
                status_code=400
            )
        return ResponseManager.handle_success_response(
            message="payment initiated successfully!",
            data=response["data"]
        )


    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="confirm-payment")
    def confirm_training_payment(self, request):
        """confirms training payment for user signing up"""
        serializer = ConfirmPaymentSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_messages,
                status_code=400
            )
        data: dict = serializer.validated_data
        response = TrainingUtil.confirm_training_payment(data)
        if not response.get("success"):
            msg = response.get("message", "Unable to confirm payment at the moment!")
            return ResponseManager.handle_error_response(
                message=msg,
                status_code=400
            )
        return ResponseManager.handle_success_response(
            message="payment confirmed successfully!",
            data=response["data"]
        )


class DashboardViewSet(ViewSet):

    authentication_classes = [ TokenAuthentication ]
    permission_classes = [ IsAuthenticated ]

    @action(detail=False, methods=["get"], url_path="training-data")
    def get_training_info(self, request):
        """dashboard training info"""
        user = request.user
        user_type = UserUtils.get_user_type(user)
        logger.debug(f"user type here!!!!!: {user_type}")
        filter_params = {"user__id": user.id}
        if user_type == "INSTRUCTOR":
            filter_params.pop("user__id")
            filter_params.update({"instructor_id": user.id})
            trainings = TrainingUtil.list_trainings(
                filter_params=filter_params, paginate=False
            )
        else:
            trainings = TrainingUtil.list_trainings(
                filter_params=filter_params, paginate=False
            )
        metrics = TrainingUtil.get_training_metrics(trainings)
        metric_serializer = TrainingMetrics(metrics, context={"user": user})
        return ResponseManager.handle_success_response(
            message="training metrics successfully retrieved!",
            data=metric_serializer.data
        )

    @action(methods=["get"], detail=False, url_path="courses")
    def get_courses(self, request):
        """gets the courses in the system"""
        user = request.user
        courses = TrainingUtil.get_total_courses(filter_params={}, paginate=False)
        if request.query_params.get("training_id"):
            courses = TrainingUtil.get_training_courses(
                request.query_params.get("training_id")
            )
        if request.query_params.get("current_user_courses"):
            course_ids = TrainingCourse.objects.filter(
                Q(user_id=user.id) | Q(training__user__id=user.id)
            ).values_list("course__id", flat=True)
            courses = courses.filter(id__in=course_ids)
        serializer = CourseSerializer(courses, many=True)
        return ResponseManager.handle_success_response(
            message="courses successfully retrieved!",
            data=serializer.data
        )

    @action(detail=False, methods=["post"], url_path="assign-courses")
    def assign_course_to_training(self, request):
        """assigns courses to the give training"""
        user = request.user
        serializer = AssignCourseSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_message
            )
        TrainingUtil.assign_training_courses(user, serializer.validated_data)
        return ResponseManager.handle_success_response(
            message="courses successfully added to training!",
            data={},
            status_code=201
        )

    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="create-assignment")
    def create_assignment(self, request):
        """creates an assignment for the given training"""
        serializer = CreateAssignmentSerializer(data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_message
            )
        user = request.user
        assignment = DashboardUtil.create_user_assignment(
            user=user, data=serializer.validated_data
        )
        serializer = AssignmentSerializer(assignment)
        return ResponseManager.handle_success_response(
            message="assignment successfully created!",
            data=serializer.data
        )

    @action(detail=False, methods=["post"], url_path="update-assignment")
    def update_assignment(self, request):
        """updates an assignment"""
        user = request.user
        serializer = UpdateAssignmentSerializer(data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_messages
            )
        assignment = DashboardUtil.update_assignment(user, serializer.validated_data)
        serializer = AssignmentSerializer(assignment)
        return ResponseManager.handle_success_response(
            message="assignment successfully updated!",
            data=serializer.data
        )

    @action(detail=False, methods=["get"], url_path="assignments")
    def get_assignments(self, request):
        """returns all the assignments"""
        user = request.user
        params = request.query_params
        assignments = DashboardUtil.list_assignments(
            user, params, paginate=True,
        )
        if not isinstance(assignments, dict):
            return ResponseManager.handle_success_response(
                message="assignments successfully retrieved!",
                data=AssignmentSerializer(assignments, many=True).data
            )
        return ResponseManager.handle_paginated_response(
            message="assignments successfully retrieved!",
            data=assignments
        )

    @action(detail=False, methods=["post"], url_path="mark-attendance")
    def mark_attendance(self, request):
        """allows student to mark his attendance of a training"""
        user = request.user
        serializer = MarkAttendanceSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_message
            )
        course = DashboardUtil.mark_attendance(
            user, serializer.validated_data
        )
        course_serializer = CourseSerializer(course)
        return ResponseManager.handle_success_response(
            message="attendance successfully marked!",
            data=course_serializer.data
        )

    @action(detail=False, methods=["get"], url_path="attendance-report")
    def get_attendance_report(self, request):
        """returns information related to the attendance of a training  and/or its courses"""
        user = request.user
        params = request.query_params
        data = DashboardUtil.get_attendance_report(user, params)
        return ResponseManager.handle_success_response(
            message="attendance report successfully retrieved!",
            data=data
        )

    @action(methods=["post"], detail=False, url_path="create-course")
    def create_course(self, request):
        """creates a course individually"""
        user = request.user
        serializer = CreateCourseSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_messages
            )
        course = DashboardUtil.create_course(user, serializer.validated_data)
        course_serializer = CourseSerializer(course)
        return ResponseManager.handle_success_response(
            message="Course Successfully created!",
            data=course_serializer.data
        )

    @action(methods=["get"], detail=False, url_path="get-course/(?P<pk>[a-z,A-Z,0-9]+)")
    def retrieve_course(self, request, pk=None):
        """single course"""
        course = DashboardUtil.retrieve_course(pk, request.user)
        serializer = CourseSerializer(course)
        return ResponseManager.handle_success_response(
            "course successfully retrieved!",
            data=serializer.data
        )
