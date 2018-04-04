#!/bin/bash
find . -path *migrations* -name "*.py" -not -path "*__init__*" -not -path "*venv*" -exec rm {} \;
find . -path "*.sqlite3" -exec rm {} \;
python manage.py makemigrations
python manage.py migrate
