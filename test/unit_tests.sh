#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DATABASE=musicbot_test
export MB_NO_AUTH=1
/usr/bin/env python -m unittest $my_dir/test.py
