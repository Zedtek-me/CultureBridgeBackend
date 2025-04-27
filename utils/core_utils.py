from typing import Type, Optional, Union, List, Dict
import random
import string
import logging

from django.db.models import Q, QuerySet
from django.db import transaction

from apps.core.models import (
    Training, PaymentTransaction, TrainingCourse,
    Course
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
