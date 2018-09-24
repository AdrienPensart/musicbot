#!/bin/sh

set -e

export MB_DB=${MB_DB:-'postgresql://postgres:musicbot@localhost:5432/musicbot_test'}
my_dir="$(dirname "$0")"
/usr/bin/env python -m unittest $my_dir/test.py
