"""
Celery Configuration and Application Instance

This module is imported by the API process. The API must be able to boot even if
Celery is not installed (e.g., minimal deployments, local dev without workers).
"""

from app.core.config import settings

try:
    from celery import Celery  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    Celery = None  # type: ignore


class _DummyCeleryApp:
    """Fallback that lets @celery_app.task be used safely."""

    def task(self, *args, **kwargs):  # noqa: D401
        def decorator(fn):
            return fn

        return decorator

    def send_task(self, *args, **kwargs):
        raise RuntimeError("Celery is not installed; background tasks are disabled.")


if Celery is None:
    celery_app = _DummyCeleryApp()
else:
    celery_app = Celery(
        "memax_worker",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["app.tasks.update_user_embedding"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        worker_prefetch_multiplier=1,
    )

    if __name__ == "__main__":
        celery_app.start()
