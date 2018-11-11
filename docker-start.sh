#!/bin/sh

/usr/bin/gunicorn -n sensu-grid --workers 3 --bind 0.0.0.0:5000 --chdir /opt/sensu-grid --reload --log-file /dev/stdout --access-logfile /dev/stdout --error-logfile /dev/stderr sensugrid:app