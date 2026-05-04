import os
from celery import Celery, Task
from django.conf import settings

from utils.helpers import logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "culturebridge.settings")


class BaseTask(Task):
    """Base task class for all Celery tasks."""

    retry_backoff = True
    autoretry_for = (Exception,)
    max_retries = 5

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.exception(f"Task {self.name} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


app = Celery(
    'culturebridge',
    include=[
        'apps.users.tasks', 'utils.email_utils',
        'apps.background_tasks.payments.tasks'
    ],
    task_cls=BaseTask,
    namespace="CELERY"
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
