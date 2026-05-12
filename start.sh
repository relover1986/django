#!/bin/bash
cd /root/django
source /root/django/venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8000 > /var/log/django.log 2>&1 &
echo "Django PID: $!"
