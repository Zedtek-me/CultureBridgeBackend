from celery import shared_task
from django.core.mail import EmailMessage
from typing import Optional

from utils.helpers import get_logger

logger = get_logger()


@shared_task(bind=False, name="send_mail_async")
def send_mail_async(
    email_msg: EmailMessage, *args, **kwargs
) -> Optional[bool]:
    """asynchronous email sender task"""
    try:
        email_msg.content_subtype = "html"
        email_msg.send(fail_silently=False)
    except Exception as e:
        logger.exception(f"Error sending email to {email_msg.to}: {e}")
        return False
    return True
