#!/bin/bash
python manage.py migrate --settings=myproject.local_settings &
python manage.py runserver --settings=myproject.local_settings
