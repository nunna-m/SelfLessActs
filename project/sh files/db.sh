#!/bin/sh
echo "[i] Sleeping 5 sec"
sleep 5

echo "Starting all process"
exec /usr/bin/mysqld --user=mysql --console

exec "$@";