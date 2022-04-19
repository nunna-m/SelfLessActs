#!/bin/sh

(nginx -g 'daemon on;' &) &&
gunicorn user.py:app --daemon