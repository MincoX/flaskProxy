#!/bin/bash

if [ ! -d "/usr/src/flaskProxy/logs" ]; then
  mkdir "/usr/src/flaskProxy/logs"
fi

celery -A celery_app worker -l info &
celery -A celery_app beat -l info &

gunicorn -c /usr/src/flaskProxy/gunicorn.py manager:app
