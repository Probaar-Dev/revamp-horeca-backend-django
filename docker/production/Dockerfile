FROM python:3.12.4-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV APP_ENV=production
ENV TZ=America/Lima

RUN : \
    && apt update \
    && apt install -y --no-install-recommends \
        locales \
        gettext \
        tzdata \
        binutils \
        libproj-dev \
        gdal-bin \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && :

WORKDIR /app

# Python and dependencies installation

USER root

COPY requirements.txt .
RUN : \
    && pip install --no-cache-dir -r requirements.txt \
    && :

COPY --chown=probaar:probaar . .

USER probaar
RUN : \
    && python manage.py collectstatic --no-input \
    && python manage.py makemessages --all \
    && python manage.py compilemessages \
    && :

USER root

RUN mkdir -p /var/log/probaar
RUN ln -sf /dev/stdout /var/log/probaar/gunicorn.access.log

USER probaar

ENTRYPOINT ["./docker/production/entrypoint.sh"]

CMD ["./docker/production/gunicorn_start.sh"]
