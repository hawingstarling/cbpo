#!/bin/sh

python /app/manage.py migrate
python /app/manage.py collectstatic --noinput
#gunicorn config.wsgi -b 0.0.0.0:8000 --chdir=/app --timeout 300
gunicorn config.wsgi -c /gunicorn.conf.py
