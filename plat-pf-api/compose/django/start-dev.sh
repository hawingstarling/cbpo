#!/bin/sh
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}"

sleep 10

python ./manage.py migrate
python manage.py runserver 0.0.0.0:8000

