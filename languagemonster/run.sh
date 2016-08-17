#!/bin/sh

git checkout test
. ~/monster/env_test.sh
python manage.py runserver 8001
