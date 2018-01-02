#!/bin/bash

my_dir="$(dirname "$0")"
AIOCACHE_DISABLE=1 $my_dir/../env/bin/python $my_dir/../musicbot --verbosity debug server --dev start --host 127.0.0.1 --port 1337
