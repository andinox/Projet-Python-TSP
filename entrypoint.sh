#!/bin/bash
set -e

export PATH="/root/.local/bin:$PATH"

cd DiagnosticTool

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/router.json fixtures/scenario.json fixtures/users.json
exec /usr/local/bin/gunicorn  DiagnosticTool.wsgi:application --workers 2 --log-level debug --bind 0.0.0.0:8080
