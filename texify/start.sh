#!/bin/bash

# Start Celery worker
celery -A manager worker --loglevel=info &

# Start flask server
gunicorn -w 1 -b 0.0.0.0:8080 app:app --log-level DEBUG
