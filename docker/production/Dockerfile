FROM python:3.12.4-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV APP_ENV=production
ENV TZ=America/Lima

ARG PGDATABASE
ARG PGUSER
ARG PGPASSWORD
ARG PGHOST
ARG PGPORT


RUN : \
    && apt update \
    && apt install -y --no-install-recommends \
        locales \
        gettext \
        tzdata \
        binutils \
        libproj-dev \
        gdal-bin \
        libicu72 \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && :

WORKDIR /app

# The 'horeca' user will be used to run the application
# The whole /app will be owned by said user
RUN mkdir -p /var/log/horeca && \
    groupadd -g 1000 horeca && \
    useradd -u 1000 -g 1000 -d /srv horeca && \
    chown -hR horeca:horeca . && \
    chown -hR horeca:horeca /var/log/horeca

# Python and dependencies installation

USER root

COPY requirements.txt .
RUN : \
    && pip install --no-cache-dir -r requirements.txt \
    && :

COPY --chown=horeca:horeca . .

USER horeca
RUN : \
    && python manage.py collectstatic --no-input \
    && python manage.py makemessages --all \
    && python manage.py compilemessages \
    && :

USER root

RUN ln -sf /dev/stdout /var/log/horeca/gunicorn.access.log

USER horeca

ENTRYPOINT ["./docker/production/entrypoint.sh"]

CMD ["./docker/production/gunicorn_start.sh"]
