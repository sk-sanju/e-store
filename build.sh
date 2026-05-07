#!/usr/bin/env bash

set -e

python -m pip install --upgrade pip
pip install Django
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate