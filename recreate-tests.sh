#!/bin/sh

set -e
trap '[ $? -eq 0 ] && exit 0 || echo "$0 FAILED"' EXIT

docker compose rm musicbot_db_test -s -f -v
docker compose create musicbot_db_test
docker compose start musicbot_db_test
