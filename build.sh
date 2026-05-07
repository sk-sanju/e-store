#!/usr/bin/env bash

set -o errexit

pip install --upgrade pip

# Clean install (VERY IMPORTANT)
pip install --no-cache-dir -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate