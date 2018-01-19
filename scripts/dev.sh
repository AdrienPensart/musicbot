#!/bin/bash

my_dir="$(dirname "$0")"
export AIOCACHE_DISABLE=1
while true; do
    $my_dir/../env/bin/python $my_dir/../musicbot --verbosity debug server --watcher --dev --autoscan start --http-host 127.0.0.1 --http-port 1337 --http-user musicbot-dev --http-password musicbot-dev
done
