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
            if EmailUtil.RETRY_COUNT > 0:
                EmailUtil.RETRY_COUNT -= 1
                return EmailUtil.send_templated_email(
                    subject, to_email, template_name, context, from_email
                )
            return False
        return True
