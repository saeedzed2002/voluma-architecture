from celery import Celery  # type: ignore[import-untyped]

from app.core.config import get_settings


def create_celery_app() -> Celery:
    settings = get_settings()
    application = Celery("voluma", broker=settings.celery_broker_url)
    application.conf.update(
        task_ignore_result=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_track_started=False,
        task_time_limit=15 * 60,
        task_soft_time_limit=12 * 60,
        broker_transport_options={"visibility_timeout": 20 * 60},
        worker_prefetch_multiplier=1,
    )
    return application


celery_app = create_celery_app()

# Import task definitions after the application exists so a standalone worker registers them.
from app.tasks import media as _media_tasks  # noqa: E402, F401
