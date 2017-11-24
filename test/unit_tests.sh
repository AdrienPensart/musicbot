#!/bin/sh

set -e

my_dir="$(dirname "$0")"
/usr/bin/env python -m unittest $my_dir/test.py
