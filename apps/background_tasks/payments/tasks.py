import os
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from utils.http_utils import HttpClient as Client
from utils.encryption_utils import encrypt_data_with_fernet
from utils.helpers import logger

from apps.core.models import PaymentPlatformToken


@shared_task(
    name="refresh-flutterwave-access-token", bind=True
)
def refresh_access_token(self):
    """
    checks to refresh access token
    from flutterwave
    """
    client_id = settings.FLUTTERWAVE_CLIENT_ID
    client_secret = settings.FLUTTERWAVE_CLIENT_SECRET
    grant_type = "client_credentials"
    token_key_name = "FLUTTERWAVE_ACCESS_TOKEN"

    current_token_info = PaymentPlatformToken.fetch_token_info("FLUTTERWAVE")
    existing_token = os.getenv(token_key_name)

    should_refresh = _should_refresh_token(existing_token, current_token_info)

    if should_refresh:
        client = Client(settings.FLUTTERWAVE_OAUTH_URL)
        response = client.post(
            "/token",
            extra_headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": grant_type
            }
        )
        logger.debug(f"response from access token generation on flutterwave::: {response}")
        if not response or response.get("status") == "failed":
            logger.error(f"unable to refresh flutterwave access token::: {response}")
            return
        token_expiry = response.get("expires_in", 600)
        access_token = response.get("access_token", "")
        encrypted_access_token = encrypt_data_with_fernet(access_token)
        if not current_token_info:
            current_token_info = PaymentPlatformToken()
        current_token_info.token = encrypted_access_token
        current_token_info.expires_in = timezone.now() + timezone.timedelta(minutes=int(float(token_expiry)/60)) #+ timezone.timedelta(seconds=token_expiry)
        current_token_info.save()


def _should_refresh_token(
    existing_token: str | None = None,
    db_token_info: PaymentPlatformToken | None = None,
    check_from_db: bool = True
) -> bool:

    if not check_from_db and not existing_token:
        return True

    if not db_token_info:
        return True

    token_expiry = db_token_info.expires_in
    time_left_to_refresh = token_expiry - timezone.now()
    # TODO: modify and fix the code below, later -- there's a logic flaw.
    if time_left_to_refresh <= timezone.timedelta(seconds=1):
        return True
    return False
