#!/bin/sh

while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Flask database upgrade failed. Retrying in 5 seconds...
    sleep 5
done
gunicorn --bind 0.0.0.0:5000 --access-logfile - --error-logfile - run_flask:app
