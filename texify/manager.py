from celery import Celery

celery_app = Celery(
    "texify",
    broker="redis://127.0.0.1:6379/0",
)
celery_app.conf.update(result_backend="redis://localhost:6379/1", include=["tasks"])
