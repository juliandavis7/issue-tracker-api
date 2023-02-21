#!/bin/bash
python manage.py migrate --settings=myproject.local_settings &
python manage.py runserver 0.0.0.0:8080 --settings=myproject.local_settings
