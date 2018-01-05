#!/bin/sh

set -e

my_dir="$(dirname "$0")"
musicbot=$my_dir/../musicbot
export MB_DATABASE=musicbot_test

python3 $musicbot db drop --yes
python3 $musicbot db create
python3 $musicbot db clear --yes
python3 $musicbot folder scan --crawl $my_dir/fixtures/*
python3 $musicbot folder find $my_dir/fixtures/*
python3 $musicbot folder rescan --crawl
python3 $musicbot db clean
python3 $musicbot youtube musics
python3 $musicbot youtube albums
python3 $musicbot folder sync tests2
rm -rf tests2
python3 $musicbot folder watch &
sleep 1
kill %%

python3 $musicbot stats
python3 $musicbot tag show
python3 $musicbot playlist new
python3 $musicbot --dry playlist bests $my_dir/fixtures
