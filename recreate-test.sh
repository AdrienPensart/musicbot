#!/bin/sh

set -e
trap '[ $? -eq 0 ] && exit 0 || echo "$0 FAILED"' EXIT

NAME=musicbot_test
docker compose down $NAME --volumes
docker compose create $NAME
docker compose start $NAME

# edgedb instance link --trust-tls-cert --non-interactive --overwrite --dsn edgedb://testuser:testpass@127.0.0.1:5657/main musicbot-test
