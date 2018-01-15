#!/bin/bash

my_dir="$(dirname "$0")"
AIOCACHE_DISABLE=1 $my_dir/../env/bin/python $my_dir/../musicbot --verbosity debug server --watcher start --http-host 127.0.0.1 --http-port 1337
