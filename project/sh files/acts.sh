#!/bin/sh

(nginx -g 'daemon on;' &) &&
gunicorn act.py:app --daemon