#!/bin/bash

while ! nc -z $HOST_NAME 5432; do
  sleep 1
done

python manage.py makemigrations
python manage.py migrate
[ -f data.json ] && python manage.py loaddata data.json

exec "$@"
