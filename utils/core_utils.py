from typing import Type, Optional, Union, List, Dict, Generic
import random
import string
import logging
from datetime import datetime, timedelta

from django.db.models import Q, QuerySet, Count, Sum
from django.db import transaction
from django.utils import timezone

from apps.core.models import (
    Training, PaymentTransaction, TrainingCourse,
    Course, Assignment
)

from utils.exception_utils import CustomException
from utils.helpers import paginate_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TrainingUtil:
    """all things training utility"""

    @classmethod
    def create_training(cls, **kwargs) -> Type[Training]:
        training = Training.objects.create(**kwargs)
        return training

    @classmethod
    def list_trainings(
        cls, search_filter: Q = Q(), filter_params: dict = dict,
        paginate: bool = True, page_count: int = 10, page_no = 1, **kwargs
    ) -> Union[List[Training], dict, QuerySet]:
        """
        fetches and paginates training data
        """
        trainings = Training.objects.filter(search_filter, **filter_params)
        if not paginate:
            return trainings
        return paginate_data(trainings, page_count, page_no)

    @classmethod
    def get_training(
        cls, search_filter: Q = Q(), filter_params: dict = dict,
        raise_exception: bool = True
    ) -> Training:
        """fetches a training that matches filter params"""
        training = Training.objects.filter(search_filter, **filter_params).first()
        if not training and raise_exception is True:
            raise CustomException("Training not found!", 404)
        return training

    @classmethod
    def process_training_payment(
        cls, **kwargs
    ):
        """connects to the payment platform for payment processing"""
        from services.payment import PaymentService

        response = PaymentService("paystack").handle_payment(**kwargs)
        return response

    @classmethod
    def get_payment_txn(
        cls, filter_params: dict, raise_exception: Optional[bool] = True, **kwargs
    ) -> Type[PaymentTransaction]:
        """fetches a payment txn by the provided filter_params"""
        p_txn = PaymentTransaction.objects.filter(**filter_params).first()
        if not p_txn and raise_exception:
            raise CustomException("PaymentTransaction object not found!", 404)
        return p_txn

    @classmethod
    def get_training_metrics(
        cls, trainings: List[Training], **kwargs
    ) -> dict:
        """returns some metrics about user's trainings"""
        metrics = {
            "total_trainings": trainings.count(),
            "completed_trainings": trainings.filter(status="COMPLETED").count(),
            "pending_trainings": trainings.filter(status="PENDING").count(),
            "in_progress_trainings": trainings.filter(status="ON_GOING").count(),
            "free_trainings": trainings.filter(_choice="FREE").count(),
            "paid_trainings": trainings.filter(_choice="PAID").count()
        }
        return metrics

    @classmethod
    def get_total_instructor_students(
        cls, instructor_id: str, **kwargs
    ) -> int:
        """total students being taken by an instructor"""
        students = (
            cls.list_trainings(filter_params={"instructor_id": instructor_id}, paginate=False)
            .values_list("user__id", flat=True)
        )
        return students.count()
    
    @classmethod
    def get_training_courses(
        cls, training_id, course_ids: Optional[List[Union[str, int]]] = None
    )-> Union[List[Course], QuerySet]:
        """returns all courses that are currently being taken by the instructor"""
        training_course_ids = (
            TrainingCourse.objects
            .filter(training__id=training_id)
            .values_list("course__id", flat=True)
        )
        courses = Course.objects.filter(id__in=training_course_ids)
        if course_ids:
            courses = courses.filter(id__in=course_ids)
        return courses

    @classmethod
    def get_total_courses(
        cls, *args, filter_params: Optional[dict] = dict,
        paginate: Optional[bool] = False, page_count = 10,
        page_no = 1, **kwargs
    ) -> Union[QuerySet, dict, List[dict]]:
        """returns all courses uploaded into the system"""
        courses = Course.objects.filter(**filter_params)
        if not paginate:
            return courses
        return paginate_data(
            courses, page_count, page_no
        )

    @classmethod
    def assign_training_courses(
        cls, user, data: dict
    ) -> Optional[TrainingCourse]:
        """creates a training course representing the assignment of courses to a training"""
        with transaction.atomic():
            training = Training.objects.get(id=data.get("training_id"))
            courses = Course.objects.filter(id__in=data.get("course_ids", []))
            training_courses = []
            for course in courses:
                training_courses.append(TrainingCourse(
                    training=training, course=course,
                    current_instructor_id=user.id, user=training.user
                ))
            result = TrainingCourse.objects.bulk_create(training_courses)
            logger.debug(f"training course creation result: {result}")
            return result


class DashboardUtil:
    """all dashboard utility"""

    @classmethod
    def create_user_assignment(
        cls, user, data: dict
    ) -> Assignment:
        """returns the dashboard data for the given user"""
        training = TrainingUtil.get_training(filter_params={"id": data.pop("training_id")})
        training_student = training.user
        data = {
            "training": training,
            "content": data.pop("description", None),
            **data
        }
        assignment = Assignment.objects.create(**data)
        assignment.instructor_id = user.id
        assignment.user_id = training_student.id
        assignment.save()
        return assignment


    @classmethod
    def list_assignments(
        cls, user, filter_params: dict = dict,
        page_count = 10, page_no = 1, paginate: bool = True
    ) -> Union[QuerySet, dict, List[dict]]:
        """returns all the assignments for the given user"""
        from apps.core.serializers import (
            AssignmentSerializer
        )

        _filter = {"user_id": user.id}
        training_id = filter_params.get("training_id")
        _all = filter_params.get("all")
        status = filter_params.get("status")
        valid_statuses = ["PENDING", "COMPLETED"]
        if status and status.upper() not in valid_statuses:
            raise CustomException(
                message="Invalid status provided!",
            )
        if status:
            _filter["status"] = status.upper()
        if _all:
            _filter.pop("user_id")
        if training_id:
            _filter["training__id"] = training_id
        assignments = Assignment.objects.filter(**_filter)
        if paginate and assignments:
            logger.debug("got into the paginate block!!!!")
            assignments = AssignmentSerializer(assignments, many=True).data
            return paginate_data(assignments, page_count, page_no)
        return assignments

    @classmethod
    def update_assignment(
        cls, user, data: dict
    ) -> Assignment:
        """updates assignments"""
        assignment_id = data.get("assignment_id")
        assignment = Assignment.objects.get(id=assignment_id)
        assignment_training = assignment.training
        update_src = data.get("update_source")
        if assignment_training.instructor_id and (
            assignment_training.instructor_id != user.id and update_src == "instructor"
        ):
            raise CustomException(
                "You are not allowed to update this assignment!",
                403
            )
        assignment.title = data.get("title", assignment.title)
        assignment.content = data.get("description", assignment.content)
        assignment.answer = data.get("answer", assignment.answer)
        assignment.status = data.get("status", assignment.status)
        if update_src == "instructor":
            assignment.instructor_id = user.id
        assignment.save()
        return assignment

    @classmethod
    def mark_attendance(
        cls, user, data: dict
    ) -> Optional[Training]:
        """allows a student to mark his attendance of a training course"""
        course_id = data.get("course_id")
        training_id = data.get("training_id")
        course = Course.objects.filter(id=course_id).first()
        training_course = TrainingCourse.objects.filter(
            course__id=course_id, training__id=training_id
        ).first()
        if not training_course:
            raise CustomException("Course not found for the given training!", 404)
        logger.debug(f"training course found: {training_course}")
        former_attendance = training_course.meta.get("attendance", {})
        note = (former_attendance.get("notes") or [])
        note.append(data.get("extra_note"))
        attendance_record = {
            "course_id": course_id,
            "training_id": training_id,
            "user_id": user.id,
            "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": note
        }
        training_course.meta["attendance"] = attendance_record
        training_course.save()
        return course

    @classmethod
    def get_attendance_report(cls, user: Type["User"], filter_params: dict) -> dict:
        """returns a dict of attendance report"""
        training_id = filter_params.get("training_id")
        training_qs = (
            TrainingUtil
            .list_trainings(filter_params={"user__id": user.id}, paginate=False)
            .annotate(
            attendance_per_training=Count("meta__attendance"))
        )
        if training_id:
            training_qs = training_qs.filter(id=training_id)
        total_attendance = training_qs\
            .aggregate(total_attendance=Sum("attendance_per_training")).get("total_attendance", 0)

        # total assignments done
        assignments = cls.list_assignments(user=user, paginate=False)
        completed_assignments = assignments.filter(status="COMPLETED").count()

        metrics = {
            "attendance": f"{total_attendance}/{training_qs.count()}",
            "homework": f"{completed_assignments}/{assignments.count()}"
        }
        return metrics
