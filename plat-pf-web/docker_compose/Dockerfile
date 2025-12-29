FROM node:12.13.1-alpine3.10

ENV user mt-web
ENV UID 1000
ENV GID 1000
USER root
RUN apk add --no-cache shadow sudo && \
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

USER $user

WORKDIR /app

COPY ./docker_compose/start.sh ./start.sh
COPY . .

RUN sudo chown -R $user:$user * && sudo chown -R $user:$user .
RUN npm install --registry http://npm-registry.channelprecision.com

EXPOSE 5000
ENTRYPOINT [ "sh" , "./start.sh" ]
