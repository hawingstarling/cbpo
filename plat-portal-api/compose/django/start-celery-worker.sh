#!/bin/sh

cd /app
# default prefork
# concurrency default with gcloud config
celery -A app.core worker -P prefork
