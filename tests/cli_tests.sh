#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DB=${MB_DB:-'postgresql://postgres:musicbot@localhost:5432/musicbot_test'}

python3 $my_dir/../musicbot db drop --yes
python3 $my_dir/../musicbot db create
python3 $my_dir/../musicbot db clear --yes
python3 $my_dir/../musicbot folder scan --crawl $my_dir/fixtures/*
python3 $my_dir/../musicbot folder find $my_dir/fixtures/*
python3 $my_dir/../musicbot folder rescan --crawl
python3 $my_dir/../musicbot db clean
python3 $my_dir/../musicbot db refresh
python3 $my_dir/../musicbot youtube musics
python3 $my_dir/../musicbot youtube albums
python3 $my_dir/../musicbot folder sync tests2
rm -rf tests2
# python3 $my_dir/../musicbot folder watch &
# sleep 1
# kill %%

python3 $my_dir/../musicbot stats show
python3 $my_dir/../musicbot tag show
python3 $my_dir/../musicbot playlist new
python3 $my_dir/../musicbot --dry playlist bests $my_dir/fixtures
