#!/bin/bash
# Cron
service cron restart
python /code/manage.py runcrons
# Django
python /code/manage.py migrate
python /code/manage.py collectstatic --noinput
python /code/manage.py runserver 0.0.0.0:8000
exec "$@"