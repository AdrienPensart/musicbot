#!/bin/sh

set -e

my_dir="$(dirname "$0")"
$my_dir/unit_tests.sh
$my_dir/functional_tests.sh
