FROM python:3.10.13

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false

WORKDIR /app
RUN pip install --upgrade pip==23.0.1
RUN pip install poetry==1.6.1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY poetry.* pyproject.toml ./
RUN poetry install --without dev
RUN pip install pyactiveresource==2.2.2

COPY ./.env.example ./config/settings/.env

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/django/start-dev.sh /start-dev.sh
RUN chmod +x /start-dev.sh

COPY ./compose/django/start-celery-worker.sh /start-celery-worker.sh
RUN chmod +x /start-celery-worker.sh

COPY ./compose/django/start-celery-worker-import-lib.sh /start-celery-worker-import-lib.sh
RUN chmod +x /start-celery-worker-import-lib.sh

COPY ./compose/django/start-celery-worker-mapping-source.sh /start-celery-worker-mapping-source.sh
RUN chmod +x /start-celery-worker-mapping-source.sh

COPY ./compose/django/start-celery-worker-sync-analysis.sh /start-celery-worker-sync-analysis.sh
RUN chmod +x /start-celery-worker-sync-analysis.sh

COPY ./compose/django/start-celery-worker-time-control.sh /start-celery-worker-time-control.sh
RUN chmod +x /start-celery-worker-time-control.sh

COPY ./compose/django/start-celery-worker-bulk.sh /start-celery-worker-bulk.sh
RUN chmod +x /start-celery-worker-bulk.sh

COPY ./compose/django/start-celery-worker-community.sh /start-celery-worker-community.sh
RUN chmod +x /start-celery-worker-community.sh

COPY ./compose/django/start-celery-worker-data-source-calculation.sh /start-celery-worker-data-source-calculation.sh
RUN chmod +x /start-celery-worker-data-source-calculation.sh

COPY ./compose/django/start-celery-worker-selling-partner.sh /start-celery-worker-selling-partner.sh
RUN chmod +x /start-celery-worker-selling-partner.sh

COPY ./compose/django/start-celery-worker-sync-data-source.sh /start-celery-worker-sync-data-source.sh
RUN chmod +x /start-celery-worker-sync-data-source.sh

COPY ./compose/django/start-celery-beat.sh /start-celery-beat.sh
RUN chmod +x /start-celery-beat.sh

COPY ./compose/django/gunicorn.sh /gunicorn.sh
RUN chmod +x /gunicorn.sh

# @TODO
# COPY ./compose/django/uvicorn.sh /uvicorn.sh
# RUN chmod +x /uvicorn.sh

COPY ./compose/django/gunicorn.conf.py /gunicorn.conf.py
RUN chmod +x /gunicorn.conf.py

COPY . .

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "/gunicorn.sh" ]
