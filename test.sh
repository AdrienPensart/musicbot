#!/bin/sh

set -e

db=musicbot_test

./musicbot db --database=$db drop
./musicbot db --database=$db create

# unit tests
# /usr/bin/env python -m unittest test.py $@

# full functional tests
./musicbot db --database=$db clear
./musicbot folder --database=$db scan tests/folder1 tests/folder2
./musicbot folder --database=$db rescan
./musicbot stats --database=$db
./musicbot tag --database=$db show
# ./musicbot consistency --database=$db
./musicbot playlist --database=$db new
./musicbot --dry playlist --database=$db bests tests
# ./musicbot fix --database=$db
