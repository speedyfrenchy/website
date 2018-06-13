#!/bin/sh
source venv/bin/activate
python compile_css.py
exec gunicorn -b :5000 --access-logfile - --error-logfile - blog:blog