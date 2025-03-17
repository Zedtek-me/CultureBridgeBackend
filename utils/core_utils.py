from typing import Type, Optional, Union, List, Dict
import random
import string

from apps.core.models import Training, PaymentTransaction

from utils.exception_utils import CustomException

class TrainingUtil:
    """all things training utility"""

    @classmethod
    def create_training(cls, **kwargs) -> Type[Training]:
        training = Training.objects.create(**kwargs)
        return training

    @classmethod
    def list_trainings(self, user, filter_params):
        """
        """

    @classmethod
    def get_training(cls, filter_params: dict, raise_exception: bool = True) -> Training:
        """fetches a training that matches filter params"""
        training = Training.objects.filter(**filter_params).first()
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
