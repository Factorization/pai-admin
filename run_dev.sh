#!/usr/bin/env bash
flask db upgrade
flask --app=run_flask.py --debug run --port=3000 --cert=adhoc
