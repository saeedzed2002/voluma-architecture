#!/bin/sh
set -eu

mkdir -p \
  /tmp/nginx/client \
  /tmp/nginx/proxy \
  /tmp/nginx/fastcgi \
  /tmp/nginx/uwsgi \
  /tmp/nginx/scgi
chown -R nginx:nginx /tmp/nginx
chmod 0700 /tmp/nginx /tmp/nginx/*

exec /docker-entrypoint.sh "$@"
