#!/bin/bash
# Start Celery worker
celery -A manager worker --loglevel=info &
# Start flask server
gunicorn -w 1 -b 0.0.0.0:9090 app:app
