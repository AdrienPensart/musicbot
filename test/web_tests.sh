#!/bin/sh

set -e

my_dir="$(dirname "$0")"
musicbot=$my_dir/../musicbot
export MB_DATABASE=musicbot_test
export MB_VERBOSITy=debug

python3 $musicbot db drop --yes
python3 $musicbot db create
python3 $musicbot folder scan --crawl $my_dir/fixtures/*
python3 $musicbot server start &
sleep 1
pid=%%

kill $pid
