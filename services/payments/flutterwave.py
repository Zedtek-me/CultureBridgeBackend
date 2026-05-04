from typing import Any
from django.conf import settings
from django.db.models import Q

from interfaces.payments import PaymentInterface

from utils.core_utils import TransactionUtil, TrainingUtil
from utils.encryption_utils import decrypt_data_with_fernet, AESOperations
from utils.http_utils import HttpClient
from utils.helpers import logger
from utils.exception_utils import CustomException

from apps.users.models import User, Profile

from apps.core.models import PaymentPlatformToken, CountryAsset


class FlutterwavePaymentService(PaymentInterface):
    """
    handles flutterwave payments
    """

    BASE_URL = settings.FLUTTERWAVE_BASE_URL

    def __init__(
        self, payment_channel: str, payment_data: dict, *args, **kwargs
    ):
        self.payment_channel: str = payment_channel
        self.payment_data: dict = payment_data
        self.client = HttpClient(
            base_url=self.BASE_URL,
            headers={
                "Content-Type": "application/json",
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
            "channel": "flutterwave",
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
        latest_token = PaymentPlatformToken.fetch_token_info("flutterwave")
        if not latest_token:
            logger.exception("flutterwave bearer token not available at the moment!")
            return {}

        decrypted_access_token = decrypt_data_with_fernet(latest_token.token)
        endpoint = "/orchestration/direct-charges"
        trxn_ref = (
            payment_data.get("txn_reference") or
            TransactionUtil.generate_transaction_ref(prefix="CLTBRGTRNTRX")
        )
        user: User = kwargs.get("user")
        card_data: dict[str, str] = self._encrypt_card_data(payment_data.get("card", {}))
        logger.debug(f"encrypted card data::::::: {card_data}")
        country_asset = self._get_country_asset(payment_data.get("country") or user.profile.country)
        extra_headers = {
            "Authorization": f"Bearer {decrypted_access_token}",
            "X-Idempotency-Key": trxn_ref,
            "X-Trace-Id": trxn_ref
        }
        payload = {
            "reference": trxn_ref,
            "amount": payment_data.get("amount"),
            "currency": country_asset.currency,
            "payment_method": {
                "type": "card",
                "card": {
                    "nonce": card_data.get("nonce"),
                    "encrypted_card_number": card_data.get("number", ""),
                    "encrypted_cvv": card_data.get("cvv"),
                    "encrypted_expiry_month": card_data.get("expiry_month"),
                    "encrypted_expiry_year": card_data.get("expiry_year")
                }
            },
            "customer": self._prep_customer_payload(user, country_asset=country_asset),
            "redirect_url": settings.CULTUREBRIDGE_REDIRECT_URL
        }
        card_payment_response = self.client.post(
            endpoint=endpoint, data=payload, extra_headers=extra_headers
        )
        logger.debug(f"flutterwave card payment response: {card_payment_response}")
        return card_payment_response


    def handle_general_payment(
        self, *args, **kwargs
    ) -> dict:
        """handles general payment"""
        return {}


    def _encrypt_card_data(
        self, card_data: dict
    ) -> dict[str, str]:
        """encrypts data with AES"""
        return AESOperations(source="FLUTTERWAVE").encrypt_data(data=card_data)


    def _fetch_user_as_flutterwave_customer(
        self, user: User, **kwargs
    ) -> dict[str, Any]:
        """
        checks if user data is available locally.
        if not, fetches from remote.
        """
        user_meta: dict | None = user.meta
        user_as_flutter_customer = user_meta and user_meta.get("customer_info", {})\
            .get("flutterwave", {}) or {}
        if user_as_flutter_customer:
            return user_as_flutter_customer
        # no user; hence, create from remote
        token = kwargs.get("token")
        payement_data = kwargs.get("payment_data", {})
        if not token:
            raise CustomException(
                "Payment option not available at the moment. Try again later!",
                status_code=502
            )
        user_profile: Profile = user.profile
        country = payement_data.get("country") or user_profile.country
        country_asset = self._get_country_asset(country)
        if not country_asset:
            raise CustomException(
                "Country asset not found!",
                status_code=404
            )
        headers = self._prep_customer_headers(token)
        payload = self._prep_customer_payload(user, country_asset=country_asset)
        endpoint = "/customers"
        response = self.client.post(
            endpoint, data=payload, extra_headers=headers
        )
        logger.debug(f"response from customer creation::: {response}")
        if not response or response.get("status", "") != "success":
            raise CustomException(
                message="Payment not available at the moment. Try again later!",
                status_code=502
            )
        customer_data = response.get("data") or {}
        self._update_user_meta_with_flutterwave_customer_info(user, customer_data)
        return customer_data


    def _prep_customer_payload(
        self, user: User, **kwargs
    ) -> dict:
        country_asset: CountryAsset = kwargs.get("country_asset")
        user_profile: Profile = user.profile
        country = country_asset.country if country_asset else user_profile.country
        payload = {
            "email": user.email,
            "name": {
                "first": user.first_name,
                "middle": user.middle_name,
                "last": user.last_name
            },
            "address": {
                "city": user_profile.city,
                "country": country,
                "line1": user_profile.address_lines[0],
                "line2": user_profile.address_lines[1],
                "postal_code": "",
                "state": user_profile.state
            },
            "phone": {
                "country_code": user_profile.phone_country_code,
                "number": user_profile.phone_main_number
            }
        }
        return payload


    def _prep_customer_headers(
        self, token: str, *args, **kwargs
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return headers


    def _update_user_meta_with_flutterwave_customer_info(
        self, user: User, customer_data: dict, *args, **kwargs
    ) -> None:
        user_meta = user.meta or {}
        existing_customer_info = user_meta.get("customer_info", {})
        existing_customer_info.update({
            "flutterwave": customer_data
        })
        user_meta["customer_info"] = existing_customer_info
        user.meta = user_meta
        user.save()


    def _get_country_asset(
        self, country: str, *args, **kwargs
    ) -> CountryAsset:
        """fetches country asset based on country name"""
        country_asset = CountryAsset.get_asset(
            search_param=(
                Q(name__icontains=country) |
                Q(country__icontains=country)
            ),
            filter_params={},
            raise_exception=True
        )
        return country_asset
