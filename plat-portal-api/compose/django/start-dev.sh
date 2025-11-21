#!/bin/sh
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

python ./manage.py migrate
python ./manage.py init_role_data # command in tenancies dir
python manage.py runserver 0.0.0.0:8000

