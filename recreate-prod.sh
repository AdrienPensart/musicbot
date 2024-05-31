#!/bin/sh

set -e
trap '[ $? -eq 0 ] && exit 0 || echo "$0 FAILED"' EXIT

NAME=musicbot_prod
docker compose down $NAME --volumes
docker compose create $NAME
docker compose start $NAME

# edgedb instance link --trust-tls-cert --non-interactive --overwrite --dsn edgedb://musicbot:musicbot@127.0.0.1:5656/main musicbot-prod
