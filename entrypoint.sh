#!/bin/sh
python manage.py migrate --no-input
python manage.py loaddata movies
exec "$@"
