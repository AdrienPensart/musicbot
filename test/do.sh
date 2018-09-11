#!/bin/sh

set -e

export MB_DATABASE=musicbot_test
export MB_DB_PASSWORD=musicbot
my_dir="$(dirname "$0")"
$my_dir/unit_tests.sh
$my_dir/cli_tests.sh
$my_dir/web_tests.sh
