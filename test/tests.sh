#!/bin/sh

set -e

export MB_DATABASE=musicbot_test
my_dir="$(dirname "$0")"
$my_dir/unit_tests.sh
$my_dir/functional_tests.sh
