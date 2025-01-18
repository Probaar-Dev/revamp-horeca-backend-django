FROM python:3.12.4-bookworm

WORKDIR /usr/src/app
USER root

RUN : \
    && apt update \
    && apt install -y --no-install-recommends \
        gettext \
        tzdata \
        binutils \
        libproj-dev \
        gdal-bin \
    && :

# Export these variables by running `export UID GID`
ARG USER_ID
ARG GROUP_ID

# This maps the 'www-data' user inside the container to the host's user.
# See <https://jtreminio.com/blog/running-docker-containers-as-current-host-user>

RUN : \
    && userdel -f www-data \
    && if getent group www-data; then groupdel www-data; fi \
    && if getent group ${GROUP_ID}; then groupdel $(getent group ${GROUP_ID} | cut -d: -f1); fi \
    && groupadd -g ${GROUP_ID} www-data \
    && useradd -l -u ${USER_ID} -g www-data www-data \
    && install -d -m 0755 -o www-data -g www-data /home/www-data \
    && :

ENV TZ=America/Lima
ENV PYTHONUNBUFFERED=1
RUN chown -hR www-data:www-data /usr/src/app
USER www-data

# Node 14.20.1 and npm installation with npm 6.14.17
#  Note that we don't install any dependencies here, since they will be
#  overwritten by the host's mounted volume. See './entrypoint.sh setup'.

ENV NODE_VERSION=14.20.1
ENV NVM_DIR /tmp/nvm
RUN mkdir $NVM_DIR

RUN : \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && npm install -g yarn \
    && :

# Python dependencies installation

COPY requirements.txt .
RUN : \
    && pip install --no-cache-dir -r requirements.txt \
    && :

ENTRYPOINT ["./docker/development/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
