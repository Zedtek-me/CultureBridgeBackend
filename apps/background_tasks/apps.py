import os
import threading
import time
from django.apps import AppConfig

class BackgroundTasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.background_tasks"

    def ready(self):
        # Do not run in management commands (migrate, shell, etc.)
        if os.environ.get("EMBED_RQ_WORKER") != "true":
            return

        def start_worker():
            time.sleep(5)  # allow app + Redis to settle

            import rq.worker

            # Disable signal handling globally for RQ
            rq.worker.Worker._install_signal_handlers = lambda self: None
            rq.timeouts.BaseDeathPenalty.setup_death_penalty = lambda self: None
            rq.timeouts.BaseDeathPenalty.cancel_death_penalty = lambda self: None

            import django_rq
            from rq import SimpleWorker

            connection = django_rq.get_connection("default")
            queue = django_rq.get_queue("default", connection=connection)

            worker = SimpleWorker(
                [queue],
                connection=connection
            )
            worker.work(logging_level="INFO")

        t = threading.Thread(target=start_worker, daemon=True)
        t.start()
