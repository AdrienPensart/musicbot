#!/bin/sh

set -e

my_dir="$(dirname "$0")"
musicbot=$my_dir/../musicbot
db=musicbot_test

python3 $musicbot db --database=$db drop
python3 $musicbot db --database=$db create
python3 $musicbot db --database=$db clear
python3 $musicbot folder --database=$db scan $my_dir/fixtures/*
python3 $musicbot folder --database=$db find $my_dir/fixtures/*
python3 $musicbot folder --database=$db rescan
python3 $musicbot db --database=$db clean
python3 $musicbot folder --database=$db sync tests2
rm -rf tests2
python3 $musicbot folder --database=$db watch &
sleep 1
kill %%

python3 $musicbot stats --database=$db
python3 $musicbot tag --database=$db show
python3 $musicbot playlist --database=$db new
python3 $musicbot --dry playlist --database=$db bests $my_dir/fixtures
python3 $musicbot server --database=$db start &
sleep 1
kill %%
