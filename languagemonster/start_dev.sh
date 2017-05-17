#!/usr/bin/env bash

. ../bin/activate
export $(cat ../../language-monster-deploy/dev_env | xargs)

redis-server &
python manage.py runserver 8000
