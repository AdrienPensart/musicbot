#!/bin/bash

export MB_DB='postgresql://postgres:musicbot@localhost:5432/musicbot_prod'
export MB_WATCHER=1
export MB_AUTOSCAN=1
export MB_SERVER_CACHE=1
export MB_CLIENT_CACHE=1
export AIOCACHE_DISABLE=1
export MB_HTTP_PASSWORD=musicbot
/home/$(/usr/bin/whoami)/.local/bin/gunicorn musicbot.lib.web.wsgi:app \
	--graceful-timeout 3 \
	--timeout 3 \
	--bind 127.0.0.1:1338 \
	--worker-class sanic.worker.GunicornWorker \
	$@
