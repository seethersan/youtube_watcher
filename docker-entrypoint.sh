#!/bin/bash
# Cron
service cron restart
python /home/app/webapp/manage.py runcrons
# Django
python /home/app/webapp/manage.py migrate
python /home/app/webapp/manage.py collectstatic --noinput
python /home/app/webapp/manage.py runserver 0.0.0.0:8000
exec "$@"