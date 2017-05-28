#!/usr/bin/env bash

. ../bin/activate
export $(cat ../../language-monster-deploy/dev_env | xargs)

# postgres
redis-server &
gulp watch &
celery -A languagemonster beat &
celery -A languagemonster worker &
python manage.py runserver 8000
