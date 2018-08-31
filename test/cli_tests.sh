#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DATABASE=musicbot_test
#export MB_DRY=1
#export MB_VERBOSITY=debug

musicbot db drop --yes
musicbot db create
musicbot db clear --yes
musicbot folder scan --crawl $my_dir/fixtures/*
musicbot folder find $my_dir/fixtures/*
musicbot folder rescan --crawl
musicbot db clean
musicbot db refresh
musicbot youtube musics
musicbot youtube albums
musicbot folder sync tests2
rm -rf tests2
# musicbot folder watch &
# sleep 1
# kill %%

musicbot stats show
musicbot tag show
musicbot playlist new
musicbot --dry playlist bests $my_dir/fixtures
