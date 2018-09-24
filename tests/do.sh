#!/bin/sh

set -e

export MB_DB=${MB_DB:-'postgresql://postgres:musicbot@localhost:5432/musicbot_test'}
export MB_DB_MAX=1
#export MB_DB_SINGLE=1
#export MB_CONCURRENCY=1
my_dir="$(dirname "$0")"
$my_dir/unit_tests.sh
$my_dir/cli_tests.sh
$my_dir/web_tests.sh
