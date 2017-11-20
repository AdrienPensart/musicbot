#!/bin/sh

set -e

db=musicbot_test

./musicbot db --database=$db drop
./musicbot db --database=$db create
./musicbot db --database=$db clear
./musicbot folder --database=$db scan tests/folder1 tests/folder2
./musicbot folder --database=$db find tests/folder1 tests/folder2
./musicbot folder --database=$db rescan
./musicbot db --database=$db clean
./musicbot folder --database=$db sync tests2
rm -rf tests2
./musicbot folder --database=$db watch &
sleep 1
kill %%

./musicbot stats --database=$db
./musicbot tag --database=$db show
# ./musicbot consistency --database=$db
./musicbot playlist --database=$db new
./musicbot --dry playlist --database=$db bests tests
./musicbot server --database=$db web &
sleep 1
kill %%
# ./musicbot fix --database=$db
