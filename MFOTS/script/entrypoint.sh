#!/bin/sh

python3 manage.py collectstatic --no-input --clear
python3 manage.py makemigrations
python3 manage.py migrate

exec "$@"
