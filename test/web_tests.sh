#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DATABASE=musicbot_test
export MB_VERBOSITy=debug

musicbot db drop --yes
musicbot db create
musicbot folder scan --crawl $my_dir/fixtures/*
musicbot server start &
pid=$!
sleep 1

kill $pid
