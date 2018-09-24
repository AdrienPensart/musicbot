#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DB=${MB_DB:-'postgresql://postgres:musicbot@localhost:5432/musicbot_test'}

python3 $my_dir/../musicbot db drop --yes
python3 $my_dir/../musicbot db create
python3 $my_dir/../musicbot folder scan --crawl $my_dir/fixtures/*
python3 $my_dir/../musicbot server start &
pid=$!
sleep 1
kill $pid
