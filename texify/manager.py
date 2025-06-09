import os
from celery import Celery

REDIS_IP = os.environ.get("REDIS_IP") or "redis"

celery_app = Celery(
    "texify",
    broker=f"redis://{REDIS_IP}:6379/0",
)
celery_app.conf.update(
    result_backend=f"redis://{REDIS_IP}:6379/1",
    include=["tasks"]
)
