from celery import Celery

celery_app = Celery(
    "texify",
    broker="redis://redis:6379/0",
)
celery_app.conf.update(result_backend="redis://redis:6379/1", include=["tasks"])
