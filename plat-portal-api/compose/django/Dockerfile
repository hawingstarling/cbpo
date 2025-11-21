FROM python:3.13.1-alpine

ENV user ps-api
ENV UID 1000
ENV GID 1000
ENV PYTHONUNBUFFERED 1
ENV PATH=$PATH:/home/$user/.local/bin
ENV PYTHONPATH=$PYTHONPATH:/home/$user/.local/bin

USER root

RUN apk add --no-cache shadow sudo bash && \
    if [ -z "`getent group $GID`" ]; then \
      addgroup -S -g $GID $user; \
    else \
      groupmod -n $user `getent group $GID | cut -d: -f1`; \
    fi && \
    if [ -z "`getent passwd $UID`" ]; then \
      adduser -S -u $UID -G $user -s /bin/sh $user; \
    else \
      usermod -l $user -g $GID -d /home/$user -m `getent passwd $UID | cut -d: -f1`; \
    fi && \
    echo "$user ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$user && \
    chmod 0440 /etc/sudoers.d/$user

RUN apk update && \
    apk add --no-cache --virtual build-deps gcc python3-dev musl-dev gcc g++ make libffi libffi-dev && \
    apk add postgresql-dev

RUN pip install --upgrade pip==24.3.1
RUN pip install --progress-bar off poetry==2.0.1
RUN pip install psycopg2 gunicorn

# prevents the output of the line "sudo: setrlimit(RLIMIT_CORE): Operation not permitted" to sudo commands
# From https://ask.fedoraproject.org/t/sudo-setrlimit-rlimit-core-operation-not-permitted/4223
USER root
RUN touch /etc/sudo.conf
RUN echo 'Set disable_coredump false' > /etc/sudo.conf

USER $user

WORKDIR /ps

COPY . .
COPY ./compose/django/* ./
COPY ./.env.example ./config/settings/.env

RUN sudo chown -R $user:$user * && sudo chown -R $user:$user .
RUN sudo chown -R $user:$user /usr/local/
RUN chmod -R u+w /usr/local/

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY poetry.* pyproject.toml ./
RUN poetry config virtualenvs.in-project true
RUN poetry install
# RUN pip install django-allauth==0.41.0
RUN pip install django-celery-beat==2.7.0
#
USER root
RUN chmod +x ./entrypoint.sh ./gunicorn.sh ./start-celery-worker.sh ./start-celery-beat.sh
USER $user

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh", "./gunicorn.sh"]