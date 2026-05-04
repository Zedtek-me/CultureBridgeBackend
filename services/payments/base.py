import logging
import requests
import random
import string

from django.conf import settings
from typing import Optional, Type, List, Union

from apps.core.models import PaymentTransaction, Training

from services.payments.squad import SquadPaymentService
from services.payments.paystack import PaystackPaymentService
from services.payments.flutterwave import FlutterwavePaymentService

from utils.exception_utils import CustomException
from utils.core_utils import TrainingUtil, TransactionUtil


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PaymentService:
    """processes all things payment"""

    PLATFORMS = {
        "paystack": f"{settings.PAYSTACK_BASE_URL}/",
        "paypal": f"{settings.PAYPAL_BASE_URL}",
        "stripe": f"{settings.STRIPE_BASE_URL}/",
        "squad": f"{settings.SQUAD_BASE_URL}/",
        "flutterwave": f"{settings.FLUTTERWAVE_BASE_URL}/"
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
        if self.platform == "paystack":
            paystack_payment_service = PaystackPaymentService(
                payment_channel=kwargs.get("option"), payment_data=kwargs
            )
            response = paystack_payment_service.handle_payment()
            return response

        if self.platform == "squad":
                # handle squad payment
                squad_payment_service = SquadPaymentService(
                    payment_channel=kwargs.get("option"), payment_data=kwargs
                )
                response = squad_payment_service.handle_payment()
                return response

        if self.platform == "flutterwave":
            flutterwave_payment_service = FlutterwavePaymentService(
                payment_channel=kwargs.get("option"), payment_data=kwargs
            )
            response = flutterwave_payment_service.handle_payment()
            return response

        raise CustomException(
            message="Payment platform not available at the moment!",
            status_code=404
        )

    def handle_paystack_payment(self, base_url: str, *args, **kwargs) -> dict:
        """paystack"""
        paystack_option = kwargs.get("option")
        training_to_pay_for = TrainingUtil.get_training(
            filter_params={
                "status": "PENDING", "payment_status": "UNPAID",
                "id": kwargs.get("training_id"),
                "user__id": kwargs.get("user_id")
            }
        )
        txn_data = {
            "amount": kwargs.get("amount"),
            "currency": kwargs.get("currency"),
            "user_id": kwargs.get("user_id"),
            "txn_reference": self.generate_txn_reference(txn_type="training_payment"),
            "description": f"Training ({training_to_pay_for.language}): CultureBridge-Payment"
        }
        charge_type = "general"
        match paystack_option:
            case "card":
                charge_type = "card"
                response = {}
            case "bank_transfer":
                charge_type = "bank_transfer"
                response = {}
            case "ussd":
                charge_type = "ussd"
                response = {}
            case _:
                base_url += "/transaction/initialize"
                payload = {
                    "email": kwargs.get("email") or (kwargs.get("user") and kwargs.get("user").email),
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
        payment_txn = TransactionUtil.create_transaction(txn_data)
        payment_txn.meta = {
            "channel": "paystack",
            "charge_type": charge_type
        }
        payment_txn.training = training_to_pay_for
        payment_txn.save()
        if (response and not response.get("status")) or (response and response.get("status") not in ("success", True)):
            payment_txn.status = "FAILED"
            payment_txn.save()
            raise CustomException(
                message="unable to process payment at the moment!"
            )
        return response

    @staticmethod
    def generate_txn_reference(txn_type: Optional[str] = "training_payment") -> str:
        """generates txn reference based on txn type"""
        if txn_type == "training_payment":
            prefix = "CLTBRGTRNTRX"
            return TransactionUtil.generate_transaction_ref(prefix=prefix)
        return TransactionUtil.generate_transaction_ref()

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
