#!/bin/sh

flask db upgrade
gunicorn --bind 0.0.0.0:3000 --access-logfile - --error-logfile - run_flask:app
