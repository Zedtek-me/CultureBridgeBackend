from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django_rq import job
from typing import Optional, Union
from concurrent.futures import ThreadPoolExecutor

from utils.helpers import get_logger

logger = get_logger()

@job
def send_mail_async(
    subject: str,
    to_email: Union[str, list],
    template_name: str,
    context: dict,
    from_email: str = None,
    retry_count: int = 3
) -> Optional[bool]:
    """asynchronous email sender task"""
    context = context or {}
    try:
        email_content = render_to_string(template_name, context)

        # Create the email message
        email = EmailMessage(
            subject=subject,
            body=email_content,
            from_email=from_email,
            to=[to_email] if isinstance(to_email, str) else to_email
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
    except Exception as e:
        logger.exception(f"Error sending email to {to_email}: {e}")
        if retry_count > 0:
            retry_count -= 1
            return send_mail_async(
                subject, to_email, template_name, context, from_email,
                retry_count=retry_count
            )
        return False
    return True

def send_mail_in_background(
    subject: str,
    to_email: Union[str, list],
    template_name: str,
    context: dict,
    from_email: str = None
) -> None:
    """sends email in background using ThreadPoolExecutor"""
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(
            send_mail_async,
            subject,
            to_email,
            template_name,
            context,
            from_email
        )
