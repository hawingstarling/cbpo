#!/bin/bash

cd /app
celery -A app.core beat -l INFO
