#!/bin/sh
python manage.py migrate --no-input
python manage.py loaddata movies
python manage.py loaddata rooms
exec "$@"
