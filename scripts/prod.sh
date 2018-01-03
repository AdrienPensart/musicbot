#!/bin/bash

my_dir="$(dirname "$0")"
export MB_DATABASE=musicbot_prod
$my_dir/../env/bin/gunicorn lib.server:app --pythonpath=$my_dir/.. --bind 127.0.0.1:1338 --worker-class sanic.worker.GunicornWorker $@
