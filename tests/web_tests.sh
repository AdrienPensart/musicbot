#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DB=${MB_DB:-'postgresql://postgres:musicbot@localhost:5432/musicbot_test'}

musicbot db drop --yes
musicbot db create
musicbot folder scan $my_dir/fixtures/*
musicbot server start &
pid=$!
sleep 1
kill $pid
