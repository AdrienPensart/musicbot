#!/bin/bash

my_dir="$(dirname "$0")"
$my_dir/../env/bin/gunicorn lib.server:app --pythonpath=$my_dir/.. --bind 127.0.0.1:1337 --worker-class sanic.worker.GunicornWorker $@
