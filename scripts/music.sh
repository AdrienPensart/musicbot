#!/bin/sh

set -e

my_dir="$(dirname "$0")"
musicbot=$my_dir/../musicbot
dst="/home/admin/music"
filter="default.filter"

python3 $musicbot folder scan "$dst"
python3 $musicbot db clean
find "$dst" -name \*.m3u -delete
python3 $musicbot $@ playlist bests --suffix '_4'   --min-rating 4.0 --filter $my_dir/$filter "$dst"
python3 $musicbot $@ playlist bests --suffix '_4.5' --min-rating 4.5 --filter $my_dir/$filter "$dst"
python3 $musicbot $@ playlist bests --suffix '_5'   --min-rating 5.0 --filter $my_dir/$filter "$dst"

for k in `python3 $musicbot tag show --fields keywords --artists Buckethead --keywords pike --min-rating 4.5 | grep -o '[a-z]\+' | sort | uniq | grep -v pike`; do
    python3 $musicbot playlist new --filter $my_dir/$filter --artists Buckethead --keywords pike --keywords $k "$dst/Buckethead/Pikes/$k.m3u"
done
