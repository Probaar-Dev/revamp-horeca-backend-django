#!/bin/bash

set -e

BASE_NAME=horeca
BASE_DIR=/app
PROJECTDIR=$BASE_DIR
SOCKFILE=$BASE_DIR/run/gunicorn.sock
LOGS_DIR=/var/log/horeca
USER=horeca
GROUP=horeca
NUM_WORKERS=3
DJANGO_WSGI_MODULE=horeca.wsgi

cd $PROJECTDIR

RUNDIR=$(dirname $SOCKFILE)
[ -d $RUNDIR ] || mkdir -p $RUNDIR

gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $BASE_NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=info \
  --bind 0.0.0.0:8000 \
  --log-file=$LOGS_DIR/gunicorn.log \
  --access-logfile=$LOGS_DIR/gunicorn.access.log \
  --timeout 120 \
  --config=${PROJECTDIR}/${BASE_NAME}/gunicorn-config.py
