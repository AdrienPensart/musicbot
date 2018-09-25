#!/bin/bash

my_dir="$(dirname "$0")"
export MB_DB='postgresql://postgres:musicbot@localhost:5432/musicbot_prod'
export MB_WATCHER=0
export MB_AUTOSCAN=1
export MB_SERVER_CACHE=0
export MB_CLIENT_CACHE=1
export AIOCACHE_DISABLE=1
export MB_HTTP_PASSWORD=musicbot
$HOME/.pyenv/shims/gunicorn lib.web.wsgi:app \
	--pythonpath=$my_dir/.. \
	--bind 127.0.0.1:1338 \
	--worker-class sanic.worker.GunicornWorker \
	$@
