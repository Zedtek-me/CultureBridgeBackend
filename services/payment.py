import logging
import requests
import random
import string

from django.conf import settings
from typing import Optional, Type, List, Union

from apps.core.models import PaymentTransaction, Training

from utils.exception_utils import CustomException
from utils.core_utils import TrainingUtil


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PaymentService:
    """processes all things payment"""

    PLATFORMS = {
        "paystack": f"{settings.PAYSTACK_BASE_URL}/",
        "paypal": f"{settings.PAYPAL_BASE_URL}",
        "stripe": f"{settings.STRIPE_BASE_URL}/"
    }

    def __init__(self, platform: str, *args, **kwargs) -> Union[CustomException, None]:
        if str(platform).lower() not in self.PLATFORMS:
            raise CustomException(
                message=f"invalid payment platform provided! {platform}"
            )
        self.platform = platform.lower()

    @staticmethod
    def initiate_request(
        url: str, method: str = "GET", data: Optional[dict] = None,
        extra_headers: Optional[dict] = dict
    ):
        """initiates and parses request using a parser"""
        headers = {
            "Content-Type": "application/json"
        }
        if extra_headers:
            headers = {**headers, **extra_headers}
        if method == "POST":
            response = requests.request(method, url, json=data, headers=headers)
        else:
            response = requests.request(method, url, params=data, headers=headers)
        return PaymentService._parse_response(response)

    @staticmethod
    def _parse_response(raw_response: requests.Response) -> Union[dict, str, tuple]:
        """parses raw response into appropriate python type"""
        try:
            return raw_response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            return {
                "status": "error",
                "message": f"{e.args[0]}"
            }

    def handle_payment(self, *args, **kwargs)-> Union[tuple, str, dict]:
        """handles according to platforms"""
        base_url = self.PLATFORMS.get(self.platform)
        if self.platform == "paystack":
            response = self.handle_paystack_payment(base_url, *args, **kwargs)
            access_code, auth_url = (
                response.get("data", {}).get("access_code"),
                response.get("data", {}).get("authorization_url")
            )
            return access_code, auth_url
        raise CustomException(
            message="Payment platform not available at the moment!",
            status_code=404
        )

    def handle_paystack_payment(self, base_url: str, *args, **kwargs) -> Optional[tuple]:
        """paystack"""
        paystack_option = kwargs.get("option")
        training_to_pay_for = TrainingUtil.get_training(
            {
                "status": "PENDING", "payment_status": "UNPAID",
                "training__id": kwargs.get("training_id"),
                "user__id": kwargs.get("user_id")
            }
        )
        txn_data = {
            "amount": kwargs.get("amount"),
            "currency": kwargs.get("currency"),
            "user_id": kwargs.get("user_id"),
            "txn_reference": self.generate_txn_reference(txn_type="training_payment")
        }
        charge_type = "general"
        match paystack_option:
            case "card":
                charge_type = "card"
                response = ""
            case "bank_transfer":
                charge_type = "bank_transfer"
                response = ""
            case "ussd":
                charge_type = "ussd"
                response = ""
            case _:
                base_url += "/transaction/initialize"
                payload = {
                    "email": kwargs.get("email"),
                    "amount": kwargs.get("amount"),
                    "callback_url": f"{settings.PAYSTACK_CALLBACK_URL}/paystack-events",
                    "reference": txn_data["txn_reference"],
                    "channels": ["card", "bank", "apple_pay", "ussd", "qr", "mobile_money", "bank_transfer", "eft"]
                }
                headers = {
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
                }
                response = self.initiate_request(
                    url=base_url, method="POST", data=payload, extra_headers=headers
                )
                logger.debug(f"paystack response: {response}")
        payment_txn = self.create_transaction(txn_data)
        payment_txn.meta = {
            "channel": "paystack",
            "charge_type": charge_type
        }
        payment_txn.training = training_to_pay_for
        payment_txn.save()
        if (response and not response.get("status")) or response.get("status") not in ("success", True):
            payment_txn.status = "FAILED"
            payment_txn.save()
            raise CustomException(
                message="unable to process payment at the moment!"
            )
        return response

    @staticmethod
    def create_transaction(
        data: dict
    ) -> Type[PaymentTransaction]:
        """records a transaction"""
        return PaymentTransaction.objects.create(**data)

    @staticmethod
    def generate_txn_reference(txn_type: Optional[str] = "training_payment") -> str:
        """generates txn reference based on txn type"""
        ref = "".join(
            random.choices(string.ascii_letters + string.digits, k=32)
        )
        if txn_type == "training_payment":
            ref = "TRNG-" + ref
        return ref

    def verify_txn_status(self, ref: str, **kwargs) -> Union[dict, str, tuple]:
        """verifies txn status (platform agnostic)"""
        if self.platform == "paystack":
            base_url = self.PLATFORMS.get(self.platform)
            base_url += "/transaction/verify/%s"%ref
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
            }
            response = self.initiate_request(
                base_url, extra_headers=headers
            )
            if not (response.get("status") or response.get("status") not in ("success", True)):
                raise CustomException("Error verifying payment transaction.", 500)
            return response
        raise CustomException("Payment platform not available at the moment!", 503)
