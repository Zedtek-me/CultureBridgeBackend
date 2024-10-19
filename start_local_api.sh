#!bin/sh

echo "running migrations>>>>>>>>>>>>>>>"
python3 -m manage makemigrations --no-input
python3 -m manage migrate --no-input

echo "starting server>>>>>>>>>>>>>>>>>>"

exec gunicorn  culturebridge.wsgi:application --bind 0.0.0.0:8001 --workers=2 --log-file -