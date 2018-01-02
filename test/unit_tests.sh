#!/bin/sh

set -e

my_dir="$(dirname "$0")"
export MB_DATABASE=musicbot_test
/usr/bin/env python -m unittest $my_dir/test.py
