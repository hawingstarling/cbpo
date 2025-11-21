#!/bin/sh

python /app/manage.py migrate
python /app/manage.py collectstatic --noinput
gunicorn config.asgi:application -b 0.0.0.0:8000 --chdir=/app --timeout 300 -k uvicorn.workers.UvicornWorker