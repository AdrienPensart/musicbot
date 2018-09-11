#!/bin/sh

set -e

export MB_DATABASE=musicbot_test
export MB_DB_PASSWORD=musicbot
my_dir="$(dirname "$0")"
/usr/bin/env python -m unittest $my_dir/test.py
