from django.conf import settings

from interfaces.payments import PaymentInterface

from utils.http_utils import HttpClient
from utils.core_utils import TransactionUtil, TrainingUtil
from utils.helpers import get_logger

from apps.users.models import User

logger = get_logger()

class SquadPaymentService(PaymentInterface):
    BASE_URL = settings.SQUAD_BASE_URL
    SECRET_KEY = settings.SQUAD_SECRET_KEY

    def __init__(
        self, payment_channel: str, payment_data: dict, *args, **kwargs
    ):
        self.payment_channel: str = payment_channel
        self.payment_data: dict = payment_data
        self.client = HttpClient(
            base_url=self.BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.SECRET_KEY}"
            }
        )

    def handle_payment(
        self, *args, **kwargs
    ) -> dict:
        """handles squad payment"""
        response = {}
        kwargs = kwargs or self.payment_data
        training_to_pay_for = TrainingUtil.get_training(
            filter_params={
                "status__iexact": "PENDING", "payment_status": "UNPAID",
                "id": kwargs.get("training_id"),
                "user__id": kwargs.get("user_id")
            }
        )
        trxn_ref = TransactionUtil.generate_transaction_ref()
        self.payment_data.update({"transaction_reference": trxn_ref})
        trxn_data = {
            "amount": kwargs.get("amount"),
            "currency": kwargs.get("currency") or "USD",
            "user_id": kwargs.get("user_id"),
            "txn_reference": trxn_ref,
            "description": f"Training ({training_to_pay_for.language}): CultureBridge-Payment"
        }
        payment_txn = TransactionUtil.create_transaction(trxn_data)
        payment_txn.meta = {
            "channel": "squad",
            "charge_type": self.payment_channel
        }
        payment_txn.training = training_to_pay_for
        payment_txn.save()
        match self.payment_channel:
            case "card":
                response = self.handle_card_payment(self.payment_data, user=training_to_pay_for.user)
            case _:
                response = self.handle_general_payment(self.payment_data)
        if "data" not in response:
            response["data"] = {}
        response["data"]["transaction_reference"] = trxn_ref
        return response


    def handle_card_payment(
        self, payment_data: dict, **kwargs
    ) -> dict:
        """handles card payment"""
        endpoint = "/transaction/initiate/process-payment"
        trxn_ref = (
            payment_data.get("transaction_reference") or
            TransactionUtil.generate_transaction_ref(prefix="CLTBRGTRNTRX")
        )
        user: User = kwargs.get("user")
        curr = payment_data.get("currency", "USD")
        card_data = payment_data.get("card", {})
        payload = {
            "transaction_reference": trxn_ref,
            "amount": payment_data.get("amount"),
            "pass_charge": True,
            "currency": curr,
            "webhook_url": f"{settings.SQUAD_CALLBACK_URL}/squad-events",
            "card": {
                "number": card_data.get("number", ""),
                "cvv": card_data.get("cvv"),
                "expiry_month": card_data.get("expiry_month"),
                "expiry_year": card_data.get("expiry_year")
            },
            "payment_method": "card",
            "customer": {
                "name": user.username,
                "email": user.email
            },
            "redirect_url": settings.CULTUREBRIDGE_REDIRECT_URL
        }
        card_payment_response = self.client.post(endpoint=endpoint, data=payload)
        logger.debug(f"squad card payment response: {card_payment_response}")
        return card_payment_response


    def handle_general_payment(
        self, *args, **kwargs
    ) -> dict:
        """handles general payment"""
        return {}
