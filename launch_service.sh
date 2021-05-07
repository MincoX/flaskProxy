#!/bin/bash

celery -A celery_app worker -l info
celery -A celery_app beat -l info

gunicorn -c /usr/src/flaskProxy/gunicorn.py manager:app
