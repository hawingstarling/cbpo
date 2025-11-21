#!/bin/bash

cd /app
celery -A app.core worker -P prefork -c 20 -Ofair -l INFO
