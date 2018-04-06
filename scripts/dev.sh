#!/bin/bash

export AIOCACHE_DISABLE=1
export MB_DATABASE=musicbot_prod
export MB_NO_AUTH=1

while true; do
    #musicbot --verbosity debug server --dev --autoscan start --http-server dev.musicbot.ovh --http-host 127.0.0.1 --http-port 1337 --http-user musicbot --http-password musicbot
    musicbot --verbosity debug server --dev --autoscan start --http-server dev.musicbot.ovh --http-host 192.168.0.2 --http-port 1337 --http-user musicbot --http-password musicbot
    sleep 1;
done
