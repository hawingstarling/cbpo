#!/bin/sh

cd /app
# default eventlet with FETCH DATA IO
celery -A app.core worker -P eventlet -c 100 -n worker-for-io-fetch-data
