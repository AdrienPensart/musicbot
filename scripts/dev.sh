#!/bin/bash

export AIOCACHE_DISABLE=1
export MB_DB='postgresql://postgres:musicbot@localhost:5432/musicbot_prod'
export MB_NO_AUTH=1
export MB_DEBUG=1
my_dir="$(dirname "$0")"

while true; do
    $my_dir/../musicbot server start --dev --autoscan --http-server dev.musicbot.ovh --http-host 127.0.0.1   --http-port 1337 --http-user musicbot --http-password musicbot
    #$my_dir/../musicbot server start --dev --autoscan --http-server dev.musicbot.ovh --http-host 192.168.0.2 --http-port 1337 --http-user musicbot --http-password musicbot
    sleep 1;
done
