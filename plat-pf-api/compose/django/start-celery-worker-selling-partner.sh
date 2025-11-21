#!/bin/bash

cd /app
celery -A app.core worker -P prefork -c 4 -Ofair -l INFO -Q selling-partner
