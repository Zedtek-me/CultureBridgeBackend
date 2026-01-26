from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from typing import Union

from utils.helpers import get_logger

from celery import shared_task

logger = get_logger()


class EmailUtil:
    RETRY_COUNT = 3

    @shared_task(bind=True, name="send_templated_email_task")
    def send_templated_email(
        self,
        subject: str,
        to_email: Union[str, list],
        template_name: str,
        context: dict,
        from_email: str = None
    ) -> bool:
        """Sends an email using a template and context

        Args:
            subject (str): The subject of the email
            to_email (str): The recipient's email address
            template_name (str): The name of the template to use
            context (dict): The context to render the template with
            from_email (str, optional): The sender's email address. Defaults to None.
        """
        from apps.users.tasks import send_mail_async

        return send_mail_async(
            subject, to_email,
            template_name, context,
            from_email
        )
